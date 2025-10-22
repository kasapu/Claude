import os
from typing import Optional


class Settings:
    """Application configuration settings"""

    # API Settings
    API_TITLE: str = "Natural Language Query API"
    API_DESCRIPTION: str = "Convert natural language to SQL queries across multiple database platforms"
    API_VERSION: str = "1.0.0"

    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    # Anthropic API
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Query Settings
    MAX_QUERY_ROWS: int = int(os.getenv("MAX_QUERY_ROWS", "10000"))
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", "60"))  # seconds

    # Schema Cache
    SCHEMA_CACHE_TTL: int = int(os.getenv("SCHEMA_CACHE_TTL", "3600"))  # seconds (1 hour)

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    @classmethod
    def get_db_connector(cls, db_type: str, connection_params: dict):
        """Factory method to get database connector"""
        from connectors import (
            PostgreSQLConnector,
            MySQLConnector,
            SnowflakeConnector,
            DatabricksConnector
        )

        db_type = db_type.upper()

        if db_type == "POSTGRESQL":
            return PostgreSQLConnector(**connection_params)
        elif db_type == "MYSQL":
            return MySQLConnector(**connection_params)
        elif db_type == "SNOWFLAKE":
            return SnowflakeConnector(**connection_params)
        elif db_type == "DATABRICKS":
            return DatabricksConnector(**connection_params)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")


settings = Settings()
