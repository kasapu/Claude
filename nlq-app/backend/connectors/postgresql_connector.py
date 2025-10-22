import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Tuple
from .base import BaseConnector


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL database connector"""

    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432, **kwargs):
        super().__init__()
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    def connect(self):
        """Establish PostgreSQL connection"""
        if not self.connection or self.connection.closed:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )

    def disconnect(self):
        """Close PostgreSQL connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()

    def get_schema(self) -> Dict[str, Any]:
        """Retrieve PostgreSQL database schema"""
        self.connect()
        schema = {}

        with self.connection.cursor() as cursor:
            # Get all tables in public schema
            cursor.execute("""
                SELECT DISTINCT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                # Get columns for each table
                cursor.execute("""
                    SELECT
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        tc.constraint_type,
                        ccu.table_name AS foreign_table,
                        ccu.column_name AS foreign_column
                    FROM information_schema.columns c
                    LEFT JOIN information_schema.key_column_usage kcu
                        ON c.table_name = kcu.table_name
                        AND c.column_name = kcu.column_name
                    LEFT JOIN information_schema.table_constraints tc
                        ON kcu.constraint_name = tc.constraint_name
                    LEFT JOIN information_schema.constraint_column_usage ccu
                        ON tc.constraint_name = ccu.constraint_name
                    WHERE c.table_schema = 'public'
                        AND c.table_name = %s
                    ORDER BY c.ordinal_position
                """, (table_name,))

                columns = []
                for row in cursor.fetchall():
                    column_info = {
                        'name': row[0],
                        'type': row[1],
                        'nullable': row[2] == 'YES',
                        'default': row[3],
                        'primary_key': row[4] == 'PRIMARY KEY',
                        'foreign_key': f"{row[5]}.{row[6]}" if row[5] else None
                    }
                    columns.append(column_info)

                schema[table_name] = {'columns': columns}

        return schema

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        self.connect()

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)

            # Check if query returns results
            if cursor.description:
                return [dict(row) for row in cursor.fetchall()]
            else:
                return []

    def validate_query(self, sql: str) -> Tuple[bool, str]:
        """Validate SQL query using EXPLAIN"""
        self.connect()

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"EXPLAIN {sql}")
                return True, "Query is valid"
            except Exception as e:
                return False, str(e)
