from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import time
import logging
from typing import Dict, Any

# Import from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from models import (
    QueryRequest, QueryResponse, SchemaResponse,
    HealthResponse, RefineQueryRequest, ConnectionRequest
)
from core import NLQProcessor, QueryValidator
from connectors import (
    PostgreSQLConnector, MySQLConnector,
    SnowflakeConnector, DatabricksConnector
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NLQ Processor
nlq_processor = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global nlq_processor

    logger.info("Starting Natural Language Query API...")

    # Validate settings
    try:
        settings.validate()
        nlq_processor = NLQProcessor(api_key=settings.ANTHROPIC_API_KEY)
        logger.info("NLQ Processor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NLQ Processor: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Natural Language Query API...")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.API_VERSION
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.API_VERSION
    )


@app.post("/api/query", response_model=QueryResponse)
async def execute_nlq_query(request: QueryRequest):
    """
    Execute a natural language query

    This endpoint converts natural language questions into SQL queries
    and optionally executes them against the specified database.
    """
    start_time = time.time()

    try:
        logger.info(f"Processing query: {request.question}")

        # Get database connector
        db_connector = get_connector(request.db_type.value, request.connection_params)

        # Connect to database
        db_connector.connect()

        # Get database schema
        logger.info("Retrieving database schema...")
        schema = db_connector.get_schema()
        logger.info(f"Retrieved schema with {len(schema)} tables")

        # Process natural language query
        logger.info("Processing natural language query...")
        nlq_result = nlq_processor.process_query(
            user_query=request.question,
            db_schema=schema,
            db_type=request.db_type.value.upper()
        )

        if not nlq_result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=nlq_result.get('error', 'Failed to process query')
            )

        sql_query = nlq_result['sql']

        # Validate query safety
        is_safe, safety_msg = QueryValidator.validate_safety(sql_query)
        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Query safety validation failed: {safety_msg}"
            )

        # Enforce row limit
        sql_query = QueryValidator.enforce_row_limit(sql_query, settings.MAX_QUERY_ROWS)

        # Execute query if requested
        results = None
        row_count = None

        if request.execute:
            logger.info("Validating SQL query...")
            is_valid, validation_msg = db_connector.validate_query(sql_query)

            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SQL validation failed: {validation_msg}"
                )

            logger.info("Executing SQL query...")
            results = db_connector.execute_query(sql_query)
            row_count = len(results)
            logger.info(f"Query executed successfully, returned {row_count} rows")

        # Calculate execution time
        execution_time = time.time() - start_time

        # Close database connection
        db_connector.disconnect()

        return QueryResponse(
            success=True,
            sql=sql_query,
            explanation=nlq_result.get('explanation'),
            assumptions=nlq_result.get('assumptions', []),
            complexity=nlq_result.get('complexity'),
            results=results,
            row_count=row_count,
            execution_time=execution_time,
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/refine", response_model=QueryResponse)
async def refine_query(request: RefineQueryRequest):
    """
    Refine an existing SQL query

    This endpoint takes an existing SQL query and refinement instructions,
    then generates an improved version of the query.
    """
    try:
        logger.info(f"Refining query with instruction: {request.refinement}")

        # Process refinement
        nlq_result = nlq_processor.refine_query(
            original_sql=request.original_sql,
            refinement_request=request.refinement,
            db_type=request.db_type.value.upper()
        )

        if not nlq_result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=nlq_result.get('error', 'Failed to refine query')
            )

        return QueryResponse(
            success=True,
            sql=nlq_result['sql'],
            explanation=nlq_result.get('explanation'),
            assumptions=nlq_result.get('assumptions', []),
            complexity=nlq_result.get('complexity'),
            results=None,
            row_count=None,
            execution_time=None,
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refining query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/schema", response_model=SchemaResponse)
async def get_database_schema(request: ConnectionRequest):
    """
    Retrieve database schema

    This endpoint connects to the specified database and retrieves
    its schema including tables, columns, and relationships.
    """
    try:
        logger.info(f"Retrieving schema for {request.db_type.value} database")

        # Get database connector
        db_connector = get_connector(request.db_type.value, request.connection_params)

        # Connect and get schema
        db_connector.connect()
        schema = db_connector.get_schema()
        db_connector.disconnect()

        logger.info(f"Successfully retrieved schema with {len(schema)} tables")

        return SchemaResponse(
            success=True,
            schema=schema,
            table_count=len(schema),
            error=None
        )

    except Exception as e:
        logger.error(f"Error retrieving schema: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/test-connection")
async def test_database_connection(request: ConnectionRequest):
    """
    Test database connection

    This endpoint tests whether the provided connection parameters
    can successfully connect to the database.
    """
    try:
        logger.info(f"Testing connection to {request.db_type.value} database")

        # Get database connector
        db_connector = get_connector(request.db_type.value, request.connection_params)

        # Test connection
        is_connected, message = db_connector.test_connection()

        if is_connected:
            db_connector.disconnect()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"success": True, "message": message}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": message}
            )

    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "message": str(e)}
        )


@app.get("/api/examples")
async def get_example_queries():
    """
    Get example natural language queries

    This endpoint returns a list of example queries that users can try.
    """
    examples = [
        {
            "category": "Customer Analytics",
            "queries": [
                "What was our customer acquisition cost by channel last quarter?",
                "Show me new customer growth month by month this year",
                "Which marketing channels brought in the most high-value customers?",
                "What's our customer churn rate this quarter vs last quarter?"
            ]
        },
        {
            "category": "Revenue Performance",
            "queries": [
                "What was total revenue by product category in Q4?",
                "Show me year-over-year revenue growth by region",
                "Which products have the highest revenue per customer?",
                "What's our monthly recurring revenue trend for the last 12 months?"
            ]
        },
        {
            "category": "Financial Performance",
            "queries": [
                "What are our top 10 products by profit margin?",
                "Show me gross margin trend by quarter for the last 2 years",
                "Which business units are most profitable?",
                "What are our largest expense categories this quarter?"
            ]
        },
        {
            "category": "Sales Analytics",
            "queries": [
                "Who are our top 10 sales reps by revenue this quarter?",
                "What's our average deal size by sales region?",
                "Show me win rate by sales stage",
                "What's the total value of deals in our pipeline by stage?"
            ]
        },
        {
            "category": "Operational Efficiency",
            "queries": [
                "What's our average order fulfillment time by warehouse?",
                "Which products have the longest delivery times?",
                "Show me on-time delivery rate by shipping carrier",
                "What's our average customer support ticket resolution time?"
            ]
        }
    ]

    return {"examples": examples}


def get_connector(db_type: str, connection_params: Dict[str, Any]):
    """
    Factory function to get database connector

    Args:
        db_type: Database type (postgresql, mysql, snowflake, databricks)
        connection_params: Connection parameters

    Returns:
        Database connector instance
    """
    db_type_upper = db_type.upper()

    if db_type_upper == "POSTGRESQL":
        return PostgreSQLConnector(**connection_params)
    elif db_type_upper == "MYSQL":
        return MySQLConnector(**connection_params)
    elif db_type_upper == "SNOWFLAKE":
        return SnowflakeConnector(**connection_params)
    elif db_type_upper == "DATABRICKS":
        return DatabricksConnector(**connection_params)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
