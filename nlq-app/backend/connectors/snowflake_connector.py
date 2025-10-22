import snowflake.connector
from typing import Dict, List, Any, Tuple
from .base import BaseConnector


class SnowflakeConnector(BaseConnector):
    """Snowflake database connector"""

    def __init__(self, account: str, user: str, password: str,
                 warehouse: str, database: str, schema: str = 'PUBLIC', **kwargs):
        super().__init__()
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.schema = schema

    def connect(self):
        """Establish Snowflake connection"""
        if not self.connection:
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )

    def disconnect(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_schema(self) -> Dict[str, Any]:
        """Retrieve Snowflake database schema"""
        self.connect()
        schema_dict = {}

        cursor = self.connection.cursor()

        # Get all tables in the schema
        cursor.execute(f"""
            SELECT table_name
            FROM {self.database}.information_schema.tables
            WHERE table_schema = '{self.schema}'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        for table_name in tables:
            # Get columns for each table
            cursor.execute(f"""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM {self.database}.information_schema.columns
                WHERE table_schema = '{self.schema}'
                    AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """)

            columns = []
            for row in cursor.fetchall():
                column_info = {
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'primary_key': False,  # Will be updated below
                    'foreign_key': None
                }
                columns.append(column_info)

            # Get primary keys
            cursor.execute(f"""
                SHOW PRIMARY KEYS IN TABLE {self.database}.{self.schema}.{table_name}
            """)
            pk_columns = {row[4] for row in cursor.fetchall()}  # column_name is in position 4

            # Update primary key info
            for col in columns:
                if col['name'] in pk_columns:
                    col['primary_key'] = True

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
