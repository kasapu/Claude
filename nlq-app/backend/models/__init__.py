from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class DatabaseType(str, Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SNOWFLAKE = "snowflake"
    DATABRICKS = "databricks"


class ConnectionRequest(BaseModel):
    """Database connection parameters"""
    db_type: DatabaseType = Field(..., description="Type of database")
    connection_params: Dict[str, str] = Field(..., description="Connection parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "db_type": "postgresql",
                "connection_params": {
                    "host": "localhost",
                    "database": "analytics",
                    "user": "analyst",
                    "password": "password",
                    "port": "5432"
                }
            }
        }


class QueryRequest(BaseModel):
    """Natural language query request"""
    question: str = Field(..., min_length=1, description="Natural language question")
    db_type: DatabaseType = Field(..., description="Database type")
    connection_params: Dict[str, str] = Field(..., description="Database connection parameters")
    execute: bool = Field(default=True, description="Whether to execute the query or just generate SQL")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What was our customer acquisition cost by channel last quarter?",
                "db_type": "postgresql",
                "connection_params": {
                    "host": "localhost",
                    "database": "analytics",
                    "user": "analyst",
                    "password": "password"
                },
                "execute": True
            }
        }


class QueryResponse(BaseModel):
    """Query response with SQL and results"""
    success: bool = Field(..., description="Whether the query was successful")
    sql: Optional[str] = Field(None, description="Generated SQL query")
    explanation: Optional[str] = Field(None, description="Plain-English explanation")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    complexity: Optional[str] = Field(None, description="Query complexity (Low/Medium/High)")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    row_count: Optional[int] = Field(None, description="Number of rows returned")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if query failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "sql": "SELECT channel, SUM(spend) / COUNT(customers) as cac FROM marketing GROUP BY channel",
                "explanation": "This query calculates customer acquisition cost by dividing total spend by customer count for each channel",
                "assumptions": ["Marketing data is in 'marketing' table"],
                "complexity": "Medium",
                "results": [{"channel": "Google Ads", "cac": 45.50}],
                "row_count": 5,
                "execution_time": 0.234,
                "error": None
            }
        }


class SchemaResponse(BaseModel):
    """Database schema response"""
    success: bool = Field(..., description="Whether schema retrieval was successful")
    schema: Optional[Dict[str, Any]] = Field(None, description="Database schema")
    table_count: Optional[int] = Field(None, description="Number of tables")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


class RefineQueryRequest(BaseModel):
    """Request to refine an existing query"""
    original_sql: str = Field(..., description="Original SQL query to refine")
    refinement: str = Field(..., description="Refinement instructions")
    db_type: DatabaseType = Field(..., description="Database type")

    class Config:
        json_schema_extra = {
            "example": {
                "original_sql": "SELECT * FROM customers",
                "refinement": "Add a filter for customers created in the last 30 days",
                "db_type": "postgresql"
            }
        }
