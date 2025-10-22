# Natural Language Query (NLQ) System

> Transform natural language questions into SQL queries instantly. Democratize data access for 80% of your workforce.

## Overview

The NLQ System is an enterprise-grade AI-powered application that converts plain English questions into optimized SQL queries across multiple database platforms. Built with Claude AI, it enables non-technical users to access business-critical data without SQL knowledge or IT support.

### Key Features

- **Multi-Database Support**: PostgreSQL, MySQL, Snowflake, and Databricks
- **AI-Powered**: Leverages Claude Sonnet 4.5 for 70-85% query accuracy
- **Real-Time Performance**: Sub-5-second query generation and execution
- **Production-Ready UI**: Modern, responsive web interface
- **Enterprise Security**: SQL injection protection, row limits, read-only queries
- **Query Refinement**: Iterative query improvement based on user feedback

## Architecture

```
┌─────────────────┐
│   Web UI        │ ← User asks questions in natural language
│  (Frontend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │ ← REST API endpoints
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Claude  │ │  Database    │
│   AI    │ │  Connectors  │
└─────────┘ └──────┬───────┘
                   │
         ┌─────────┴─────────┐
         ▼         ▼         ▼
    ┌──────┐  ┌──────┐  ┌──────┐
    │ PG   │  │MySQL │  │Snowf.│
    └──────┘  └──────┘  └──────┘
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Access to at least one supported database

### Installation

1. **Clone the repository**
   ```bash
   cd nlq-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

5. **Start the backend server**
   ```bash
   cd backend/api
   python main.py
   ```
   Server will start at `http://localhost:8000`

6. **Open the frontend**
   ```bash
   # In a new terminal
   cd frontend/public
   python -m http.server 3000
   ```
   Open browser to `http://localhost:3000`

## Configuration

### Environment Variables

Edit `.env` file in the root directory:

```env
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional
HOST=0.0.0.0
PORT=8000
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_QUERY_ROWS=10000
QUERY_TIMEOUT=60
SCHEMA_CACHE_TTL=3600
LOG_LEVEL=INFO
```

### Database Connection Examples

#### PostgreSQL
```json
{
  "host": "localhost",
  "port": "5432",
  "database": "analytics",
  "user": "analyst",
  "password": "your_password"
}
```

#### MySQL
```json
{
  "host": "localhost",
  "port": "3306",
  "database": "business_data",
  "user": "analyst",
  "password": "your_password"
}
```

#### Snowflake
```json
{
  "account": "your-account",
  "warehouse": "COMPUTE_WH",
  "database": "ANALYTICS_DB",
  "schema": "PUBLIC",
  "user": "analyst",
  "password": "your_password"
}
```

#### Databricks
```json
{
  "server_hostname": "your-workspace.cloud.databricks.com",
  "http_path": "/sql/1.0/warehouses/abc123",
  "access_token": "dapi..."
}
```

## Usage

### Web Interface

1. **Connect to Database**
   - Select your database type
   - Enter connection parameters
   - Click "Test Connection" to verify

2. **Ask Questions**
   - Type your question in natural language
   - Click "Generate & Execute SQL" to run the query
   - Or click "Generate SQL Only" to see the query without executing

3. **View Results**
   - See the generated SQL query
   - Read the plain-English explanation
   - View query results in a data table
   - Export results to CSV

### Example Questions

**Customer Analytics**
- "What was our customer acquisition cost by channel last quarter?"
- "Show me new customer growth month by month this year"
- "Which marketing channels brought in the most high-value customers?"

**Revenue Performance**
- "What was total revenue by product category in Q4?"
- "Show me year-over-year revenue growth by region"
- "What's our monthly recurring revenue trend for the last 12 months?"

**Financial Performance**
- "What are our top 10 products by profit margin?"
- "Show me gross margin trend by quarter for the last 2 years"
- "What are our largest expense categories this quarter?"

**Sales Analytics**
- "Who are our top 10 sales reps by revenue this quarter?"
- "What's the total value of deals in our pipeline by stage?"
- "Show me win rate by sales stage"

## API Documentation

### Endpoints

#### `POST /api/query`
Execute a natural language query

**Request Body:**
```json
{
  "question": "What was our revenue last quarter?",
  "db_type": "postgresql",
  "connection_params": {...},
  "execute": true
}
```

**Response:**
```json
{
  "success": true,
  "sql": "SELECT SUM(revenue)...",
  "explanation": "This query calculates...",
  "assumptions": ["Revenue is in 'sales' table"],
  "complexity": "Low",
  "results": [...],
  "row_count": 1,
  "execution_time": 0.234
}
```

#### `POST /api/refine`
Refine an existing SQL query

#### `POST /api/schema`
Retrieve database schema

#### `POST /api/test-connection`
Test database connection

#### `GET /api/examples`
Get example queries

### Full API Documentation
Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
nlq-app/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py           # FastAPI application
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── base.py           # Base connector class
│   │   ├── postgresql_connector.py
│   │   ├── mysql_connector.py
│   │   ├── snowflake_connector.py
│   │   └── databricks_connector.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── nlq_processor.py  # Claude AI integration
│   │   └── query_validator.py
│   ├── models/
│   │   └── __init__.py       # Pydantic models
│   └── config.py             # Configuration
├── frontend/
│   └── public/
│       ├── index.html        # Main UI
│       ├── styles.css        # Styling
│       └── app.js            # Frontend logic
├── .env.example              # Environment template
├── .gitignore
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Security

### Built-in Protections

1. **Read-Only Queries**: Only SELECT queries are allowed
2. **SQL Injection Prevention**: Validates queries for dangerous operations
3. **Row Limits**: Automatic LIMIT clause enforcement (max 10,000 rows)
4. **Query Timeout**: Configurable timeout to prevent long-running queries
5. **Connection Security**: Database credentials never logged or exposed

### Best Practices

- Never commit `.env` file with real credentials
- Use database users with read-only permissions
- Implement rate limiting in production
- Use HTTPS in production environments
- Regularly rotate database credentials and API keys

## Performance Optimization

### Schema Caching
Database schemas are cached for 1 hour (configurable) to reduce connection overhead.

### Query Optimization
- Generated queries use proper indexes
- Avoid SELECT * in favor of specific columns
- Use CTEs for complex queries
- Leverage database-specific optimizations

### Monitoring
Track these metrics:
- Query accuracy rate (target: 70-85%)
- Average response time (target: <5 seconds)
- User adoption rate

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong, unique database passwords
- [ ] Configure production CORS origins
- [ ] Set up HTTPS with SSL certificates
- [ ] Implement authentication/authorization
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Create database user with read-only permissions
- [ ] Set up automated backups
- [ ] Configure CDN for frontend assets

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY nlq-system-prompt.md .

CMD ["python", "backend/api/main.py"]
```

Build and run:
```bash
docker build -t nlq-system .
docker run -p 8000:8000 --env-file .env nlq-system
```

### Cloud Deployment

#### AWS
- Deploy backend on EC2 or ECS
- Use RDS for database connections
- CloudFront for frontend CDN
- Secrets Manager for credentials

#### Azure
- Deploy on Azure App Service
- Use Azure Database services
- Azure CDN for frontend
- Key Vault for secrets

#### GCP
- Deploy on Cloud Run or App Engine
- Use Cloud SQL
- Cloud CDN for frontend
- Secret Manager for credentials

## Troubleshooting

### Common Issues

**"Connection refused" error**
- Ensure database is accessible from your network
- Check firewall rules
- Verify connection parameters

**"API key not found" error**
- Set `ANTHROPIC_API_KEY` in `.env` file
- Ensure `.env` is in the root directory
- Restart the backend server

**"Query validation failed" error**
- Check database permissions
- Ensure user has SELECT privileges
- Verify table/column names exist

**Frontend can't connect to backend**
- Update `API_BASE_URL` in `app.js` if using different ports
- Check CORS configuration in backend
- Verify both frontend and backend servers are running

## Performance Metrics

### Target KPIs
- **Query Accuracy**: 70-85%
- **Response Time**: <5 seconds
- **User Adoption**: Enable 80% of workforce
- **Productivity Gain**: 20-30% time savings

## Contributing

This is a productized accelerator designed for rapid deployment across client engagements (2-week implementation cycle).

## License

Proprietary - G2O Internal Use

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Contact your system administrator

---

**Built with Claude AI** | Democratizing Data Access Since 2024
