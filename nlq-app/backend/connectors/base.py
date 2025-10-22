from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple


class BaseConnector(ABC):
    """Base class for all database connectors"""

    def __init__(self, **kwargs):
        self.connection = None
        self.db_type = self.__class__.__name__.replace('Connector', '').upper()

    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Retrieve database schema including tables, columns, and relationships

        Returns:
            Dict with structure:
            {
                'table_name': {
                    'columns': [
                        {
                            'name': 'column_name',
                            'type': 'data_type',
                            'nullable': bool,
                            'primary_key': bool,
                            'foreign_key': 'referenced_table.column'
                        }
                    ],
                    'description': 'table description'
                }
            }
        """
        pass

    @abstractmethod
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results

        Args:
            sql: SQL query string

        Returns:
            List of dictionaries, one per row
        """
        pass

    @abstractmethod
    def validate_query(self, sql: str) -> Tuple[bool, str]:
        """
        Validate SQL query without executing

        Args:
            sql: SQL query string

        Returns:
            Tuple of (is_valid, message)
        """
        pass

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test database connection

        Returns:
            Tuple of (is_connected, message)
        """
        try:
            self.connect()
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)

    def close(self):
        """Alias for disconnect"""
        self.disconnect()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
