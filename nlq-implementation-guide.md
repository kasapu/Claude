# NLQ System Implementation Guide

## Architecture Overview

```
┌─────────────────┐
│   User Input    │ Natural language query
│   (UI Layer)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLQ Processor  │ AI model with system prompt
│  (Claude API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SQL Generator   │ Database-specific SQL
│  & Validator    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DB Connector  │ Execute query
│ (Multi-platform)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Results Display │ Format and present data
│   (UI Layer)    │
└─────────────────┘
```

---

## System Prompt Integration

### 1. Prompt Construction

```python
def build_nlq_prompt(user_query: str, db_schema: dict, db_type: str) -> str:
    """
    Constructs the complete prompt for the AI model
    """
    system_prompt = load_system_prompt()  # Load from nlq-system-prompt.md

    context = f"""
Database Type: {db_type}
Available Schema:
{format_schema(db_schema)}

User Question: {user_query}

Generate an optimized SQL query following the guidelines above.
"""

    return system_prompt + "\n\n" + context
```

### 2. Schema Context Injection

```python
def format_schema(db_schema: dict) -> str:
    """
    Formats database schema for AI context
    """
    schema_text = []

    for table_name, table_info in db_schema.items():
        schema_text.append(f"Table: {table_name}")
        schema_text.append("Columns:")

        for column in table_info['columns']:
            col_desc = f"  - {column['name']} ({column['type']})"
            if column.get('primary_key'):
                col_desc += " [PRIMARY KEY]"
            if column.get('foreign_key'):
                col_desc += f" [FK -> {column['foreign_key']}]"
            if column.get('description'):
                col_desc += f" - {column['description']}"
            schema_text.append(col_desc)

        if table_info.get('relationships'):
            schema_text.append("Relationships:")
            for rel in table_info['relationships']:
                schema_text.append(f"  - {rel}")

        schema_text.append("")

    return "\n".join(schema_text)
```

---

## Database Connectors

### Snowflake Connector

```python
import snowflake.connector
from typing import Dict, List, Any

class SnowflakeConnector:
    def __init__(self, account: str, user: str, password: str,
                 warehouse: str, database: str, schema: str):
        self.connection = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )

    def get_schema(self) -> Dict:
        """Retrieves database schema for context"""
        cursor = self.connection.cursor()

        # Get all tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = CURRENT_SCHEMA()
        """)
        tables = cursor.fetchall()

        schema = {}
        for (table_name,) in tables:
            # Get columns for each table
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)

            columns = [
                {
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'YES'
                }
                for col in cursor.fetchall()
            ]

            schema[table_name] = {'columns': columns}

        cursor.close()
        return schema

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Executes SQL and returns results"""
        cursor = self.connection.cursor()

        try:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results
        finally:
            cursor.close()

    def validate_query(self, sql: str) -> tuple[bool, str]:
        """Validates SQL without executing"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"EXPLAIN {sql}")
            return True, "Query is valid"
        except Exception as e:
            return False, str(e)
        finally:
            cursor.close()
```

### PostgreSQL Connector

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any

class PostgreSQLConnector:
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        self.connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )

    def get_schema(self) -> Dict:
        """Retrieves database schema"""
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    tc.constraint_type
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c
                    ON t.table_name = c.table_name
                LEFT JOIN information_schema.key_column_usage kcu
                    ON c.column_name = kcu.column_name
                    AND c.table_name = kcu.table_name
                LEFT JOIN information_schema.table_constraints tc
                    ON kcu.constraint_name = tc.constraint_name
                WHERE t.table_schema = 'public'
                ORDER BY t.table_name, c.ordinal_position
            """)

            schema = {}
            for row in cursor.fetchall():
                table_name = row[0]
                if table_name not in schema:
                    schema[table_name] = {'columns': []}

                schema[table_name]['columns'].append({
                    'name': row[1],
                    'type': row[2],
                    'nullable': row[3] == 'YES',
                    'constraint': row[4]
                })

            return schema

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Executes SQL and returns results as dictionaries"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            return [dict(row) for row in cursor.fetchall()]

    def validate_query(self, sql: str) -> tuple[bool, str]:
        """Validates SQL using EXPLAIN"""
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"EXPLAIN {sql}")
                return True, "Query is valid"
            except Exception as e:
                return False, str(e)
```

### MySQL Connector

```python
import mysql.connector
from typing import Dict, List, Any

class MySQLConnector:
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 3306):
        self.connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )

    def get_schema(self) -> Dict:
        """Retrieves database schema"""
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = []

            for col in cursor.fetchall():
                columns.append({
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'YES',
                    'key': col[3],
                    'default': col[4]
                })

            schema[table] = {'columns': columns}

        cursor.close()
        return schema

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Executes SQL and returns results"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results

    def validate_query(self, sql: str) -> tuple[bool, str]:
        """Validates SQL using EXPLAIN"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"EXPLAIN {sql}")
            return True, "Query is valid"
        except Exception as e:
            return False, str(e)
        finally:
            cursor.close()
```

### Databricks Connector

```python
from databricks import sql
from typing import Dict, List, Any

class DatabricksConnector:
    def __init__(self, server_hostname: str, http_path: str, access_token: str):
        self.connection = sql.connect(
            server_hostname=server_hostname,
            http_path=http_path,
            access_token=access_token
        )

    def get_schema(self) -> Dict:
        """Retrieves database schema"""
        cursor = self.connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[1] for row in cursor.fetchall()]

        schema = {}
        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = []

            for col in cursor.fetchall():
                columns.append({
                    'name': col[0],
                    'type': col[1],
                    'comment': col[2] if len(col) > 2 else None
                })

            schema[table] = {'columns': columns}

        cursor.close()
        return schema

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Executes SQL and returns results"""
        cursor = self.connection.cursor()
        cursor.execute(sql)

        columns = [desc[0] for desc in cursor.description]
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        cursor.close()
        return results

    def validate_query(self, sql: str) -> tuple[bool, str]:
        """Validates SQL using EXPLAIN"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"EXPLAIN {sql}")
            return True, "Query is valid"
        except Exception as e:
            return False, str(e)
        finally:
            cursor.close()
```

---

## AI Model Integration

### Claude API Integration

```python
import anthropic
from typing import Dict, Any

class NLQProcessor:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from file"""
        with open('nlq-system-prompt.md', 'r') as f:
            return f.read()

    def process_query(self,
                     user_query: str,
                     db_schema: Dict,
                     db_type: str) -> Dict[str, Any]:
        """
        Processes natural language query and returns SQL + metadata
        """
        # Build context
        context = f"""
Database Type: {db_type}
Available Schema:
{self._format_schema(db_schema)}

User Question: {user_query}

Please provide:
1. The SQL query
2. Plain-English explanation
3. Any assumptions made
4. Estimated complexity (Low/Medium/High)
"""

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": context}
            ]
        )

        # Parse response
        response_text = message.content[0].text

        return self._parse_response(response_text)

    def _format_schema(self, schema: Dict) -> str:
        """Formats schema for context"""
        # Implementation from earlier
        pass

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parses AI response into structured format
        """
        # Extract SQL query (between ```sql and ```)
        import re

        sql_match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
        sql_query = sql_match.group(1) if sql_match else ""

        # Extract explanation (look for "Explanation:" section)
        explanation_match = re.search(r'\*\*Explanation\*\*:(.+?)(?:\*\*|$)',
                                     response, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ""

        # Extract complexity
        complexity_match = re.search(r'Estimated Complexity\*\*:\s*(Low|Medium|High)',
                                     response)
        complexity = complexity_match.group(1) if complexity_match else "Unknown"

        return {
            'sql': sql_query,
            'explanation': explanation,
            'complexity': complexity,
            'raw_response': response
        }
```

---

## Complete Workflow

```python
from datetime import datetime
import time

class NLQSystem:
    def __init__(self, db_connector, nlq_processor):
        self.db = db_connector
        self.nlq = nlq_processor
        self.schema = None

    def initialize(self):
        """Initialize system by loading database schema"""
        print("Loading database schema...")
        self.schema = self.db.get_schema()
        print(f"Loaded {len(self.schema)} tables")

    def query(self, user_question: str) -> Dict[str, Any]:
        """
        Main query processing workflow
        """
        start_time = time.time()

        # Step 1: Process natural language
        print(f"Processing query: {user_question}")
        nlq_result = self.nlq.process_query(
            user_query=user_question,
            db_schema=self.schema,
            db_type=self.db.__class__.__name__.replace('Connector', '')
        )

        # Step 2: Validate SQL
        print("Validating generated SQL...")
        is_valid, validation_msg = self.db.validate_query(nlq_result['sql'])

        if not is_valid:
            return {
                'success': False,
                'error': f"Generated SQL is invalid: {validation_msg}",
                'sql': nlq_result['sql']
            }

        # Step 3: Execute query
        print("Executing query...")
        try:
            results = self.db.execute_query(nlq_result['sql'])
            execution_time = time.time() - start_time

            return {
                'success': True,
                'sql': nlq_result['sql'],
                'explanation': nlq_result['explanation'],
                'complexity': nlq_result['complexity'],
                'results': results,
                'row_count': len(results),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'sql': nlq_result['sql'],
                'explanation': nlq_result['explanation']
            }

# Example Usage
if __name__ == "__main__":
    # Initialize connectors
    db = PostgreSQLConnector(
        host="localhost",
        database="analytics",
        user="analyst",
        password="password"
    )

    nlq = NLQProcessor(api_key="your-anthropic-api-key")

    # Create system
    system = NLQSystem(db, nlq)
    system.initialize()

    # Process query
    result = system.query(
        "What was our customer acquisition cost by channel last quarter?"
    )

    if result['success']:
        print(f"Query executed in {result['execution_time']:.2f} seconds")
        print(f"Returned {result['row_count']} rows")
        print(f"\nSQL:\n{result['sql']}")
        print(f"\nExplanation: {result['explanation']}")
        print(f"\nResults: {result['results'][:5]}")  # First 5 rows
    else:
        print(f"Error: {result['error']}")
```

---

## UI Integration Example (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

app = FastAPI()

# Initialize NLQ system (do this at startup)
nlq_system = None

class QueryRequest(BaseModel):
    question: str
    database_type: str  # 'snowflake', 'postgresql', 'mysql', 'databricks'
    connection_params: Dict[str, str]

class QueryResponse(BaseModel):
    success: bool
    sql: str
    explanation: str
    complexity: str
    results: Optional[List[Dict[str, Any]]] = None
    row_count: Optional[int] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

@app.post("/api/query", response_model=QueryResponse)
async def execute_nlq(request: QueryRequest):
    """
    Main API endpoint for natural language queries
    """
    try:
        # Initialize database connector based on type
        if request.database_type == 'postgresql':
            db = PostgreSQLConnector(**request.connection_params)
        elif request.database_type == 'snowflake':
            db = SnowflakeConnector(**request.connection_params)
        elif request.database_type == 'mysql':
            db = MySQLConnector(**request.connection_params)
        elif request.database_type == 'databricks':
            db = DatabricksConnector(**request.connection_params)
        else:
            raise HTTPException(400, "Unsupported database type")

        # Initialize NLQ processor
        nlq = NLQProcessor(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Create system and execute
        system = NLQSystem(db, nlq)
        system.initialize()

        result = system.query(request.question)

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/example-queries")
async def get_example_queries():
    """
    Returns example queries for users
    """
    with open('nlq-example-queries.md', 'r') as f:
        return {"examples": f.read()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

---

## Performance Optimization

### 1. Schema Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class SchemaCache:
    def __init__(self, ttl_minutes: int = 60):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get_schema(self, db_connector):
        cache_key = str(db_connector)

        if cache_key in self.cache:
            schema, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.ttl:
                return schema

        # Refresh cache
        schema = db_connector.get_schema()
        self.cache[cache_key] = (schema, datetime.now())
        return schema
```

### 2. Query Result Limiting
```python
def execute_with_limit(self, sql: str, max_rows: int = 1000) -> List[Dict]:
    """
    Executes query with automatic LIMIT for safety
    """
    # Add LIMIT if not present
    if 'LIMIT' not in sql.upper():
        sql = f"{sql.rstrip(';')} LIMIT {max_rows}"

    return self.db.execute_query(sql)
```

### 3. Async Processing for Multiple Databases
```python
import asyncio

async def query_multiple_databases(question: str, databases: List):
    """
    Query multiple databases in parallel
    """
    tasks = [
        asyncio.to_thread(system.query, question)
        for system in databases
    ]

    results = await asyncio.gather(*tasks)
    return results
```

---

## Security Considerations

### 1. SQL Injection Prevention
```python
def validate_sql_safety(sql: str) -> tuple[bool, str]:
    """
    Checks for potentially dangerous SQL operations
    """
    dangerous_keywords = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER',
        'CREATE', 'INSERT', 'UPDATE', 'GRANT', 'REVOKE'
    ]

    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Dangerous operation detected: {keyword}"

    return True, "Query is safe"
```

### 2. Row Limit Enforcement
```python
MAX_ROWS = 10000  # Prevent overwhelming responses

def enforce_row_limit(sql: str) -> str:
    """
    Ensures query has reasonable LIMIT
    """
    if 'LIMIT' not in sql.upper():
        return f"{sql.rstrip(';')} LIMIT {MAX_ROWS}"
    return sql
```

### 3. Connection Pooling
```python
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_type: str, **kwargs):
    """
    Connection pool manager
    """
    if db_type == 'postgresql':
        conn = PostgreSQLConnector(**kwargs)
    # ... other types

    try:
        yield conn
    finally:
        conn.close()
```

---

## Monitoring & Analytics

### Track Query Performance
```python
class QueryMetrics:
    def __init__(self):
        self.queries = []

    def log_query(self, query_data: Dict):
        """
        Log query for analytics
        """
        self.queries.append({
            'timestamp': datetime.now(),
            'question': query_data['question'],
            'sql': query_data['sql'],
            'execution_time': query_data['execution_time'],
            'success': query_data['success'],
            'row_count': query_data.get('row_count', 0)
        })

    def get_accuracy_rate(self) -> float:
        """
        Calculate success rate
        """
        if not self.queries:
            return 0.0

        successful = sum(1 for q in self.queries if q['success'])
        return (successful / len(self.queries)) * 100

    def get_avg_response_time(self) -> float:
        """
        Calculate average response time
        """
        if not self.queries:
            return 0.0

        total_time = sum(q['execution_time'] for q in self.queries)
        return total_time / len(self.queries)
```

---

## Testing Strategy

### Unit Tests
```python
import pytest

def test_nlq_processor():
    processor = NLQProcessor(api_key="test-key")

    # Mock database schema
    schema = {
        'customers': {
            'columns': [
                {'name': 'id', 'type': 'int'},
                {'name': 'name', 'type': 'varchar'}
            ]
        }
    }

    result = processor.process_query(
        "How many customers do we have?",
        schema,
        "postgresql"
    )

    assert 'COUNT' in result['sql'].upper()
    assert 'customers' in result['sql'].lower()

def test_query_validation():
    # Test SQL injection prevention
    sql = "SELECT * FROM users; DROP TABLE users;"
    is_safe, msg = validate_sql_safety(sql)
    assert not is_safe
    assert 'DROP' in msg
```

---

## Deployment Checklist

- [ ] Set up database connectors for all platforms
- [ ] Configure API keys securely (environment variables)
- [ ] Implement schema caching
- [ ] Add query result limits
- [ ] Enable SQL injection protection
- [ ] Set up monitoring and logging
- [ ] Create UI with query history
- [ ] Add export functionality (CSV, Excel, JSON)
- [ ] Implement user authentication
- [ ] Configure rate limiting
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Create user documentation
- [ ] Establish SLA monitoring (sub-5-second target)

---

## 2-Week Implementation Timeline

### Week 1: Core Development
- Days 1-2: Set up database connectors
- Days 3-4: Integrate Claude API with system prompt
- Day 5: Build query processing pipeline

### Week 2: UI & Testing
- Days 6-7: Create web UI
- Days 8-9: Testing and validation
- Day 10: Deployment and documentation

This accelerator can be deployed across multiple client engagements with minimal customization!
