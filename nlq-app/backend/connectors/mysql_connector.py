import mysql.connector
from typing import Dict, List, Any, Tuple
from .base import BaseConnector


class MySQLConnector(BaseConnector):
    """MySQL database connector"""

    def __init__(self, host: str, database: str, user: str, password: str, port: int = 3306, **kwargs):
        super().__init__()
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    def connect(self):
        """Establish MySQL connection"""
        if not self.connection or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )

    def disconnect(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def get_schema(self) -> Dict[str, Any]:
        """Retrieve MySQL database schema"""
        self.connect()
        schema = {}

        cursor = self.connection.cursor(dictionary=True)

        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]

        for table_name in tables:
            # Get columns for each table
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = []

            for col in cursor.fetchall():
                column_info = {
                    'name': col['Field'],
                    'type': col['Type'],
                    'nullable': col['Null'] == 'YES',
                    'default': col['Default'],
                    'primary_key': col['Key'] == 'PRI',
                    'foreign_key': None  # MySQL DESCRIBE doesn't show FK relationships
                }
                columns.append(column_info)

            # Get foreign key information
            cursor.execute(f"""
                SELECT
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME = %s
                    AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (self.database, table_name))

            fk_info = {row['COLUMN_NAME']: f"{row['REFERENCED_TABLE_NAME']}.{row['REFERENCED_COLUMN_NAME']}"
                      for row in cursor.fetchall()}

            # Update columns with FK info
            for col in columns:
                if col['name'] in fk_info:
                    col['foreign_key'] = fk_info[col['name']]

            schema[table_name] = {'columns': columns}

        cursor.close()
        return schema

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        self.connect()

        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(sql)

            # Check if query returns results
            if cursor.description:
                results = cursor.fetchall()
                return results
            else:
                return []
        finally:
            cursor.close()

    def validate_query(self, sql: str) -> Tuple[bool, str]:
        """Validate SQL query using EXPLAIN"""
        self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(f"EXPLAIN {sql}")
            return True, "Query is valid"
        except Exception as e:
            return False, str(e)
        finally:
            cursor.close()
