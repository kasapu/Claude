from databricks import sql
from typing import Dict, List, Any, Tuple
from .base import BaseConnector


class DatabricksConnector(BaseConnector):
    """Databricks SQL connector"""

    def __init__(self, server_hostname: str, http_path: str, access_token: str, **kwargs):
        super().__init__()
        self.server_hostname = server_hostname
        self.http_path = http_path
        self.access_token = access_token

    def connect(self):
        """Establish Databricks connection"""
        if not self.connection:
            self.connection = sql.connect(
                server_hostname=self.server_hostname,
                http_path=self.http_path,
                access_token=self.access_token
            )

    def disconnect(self):
        """Close Databricks connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_schema(self) -> Dict[str, Any]:
        """Retrieve Databricks database schema"""
        self.connect()
        schema_dict = {}

        cursor = self.connection.cursor()

        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [row[1] for row in cursor.fetchall()]  # table name is in position 1

        for table_name in tables:
            # Get columns for each table
            cursor.execute(f"DESCRIBE TABLE {table_name}")
            columns = []

            for row in cursor.fetchall():
                # Skip partition information and empty rows
                if row[0] and not row[0].startswith('#'):
                    column_info = {
                        'name': row[0],
                        'type': row[1],
                        'nullable': True,  # Databricks doesn't provide nullable info via DESCRIBE
                        'comment': row[2] if len(row) > 2 else None,
                        'primary_key': False,
                        'foreign_key': None
                    }
                    columns.append(column_info)

            schema_dict[table_name] = {'columns': columns}

        cursor.close()
        return schema_dict

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)

            # Get column names
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

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
