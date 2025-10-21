# NLQ System - Quick Start Guide

Get up and running with the Natural Language Query system in under 5 minutes!

## Prerequisites

- Python 3.8+
- Anthropic API Key
- Database credentials (PostgreSQL, MySQL, Snowflake, or Databricks)

## Setup Steps

### 1. Install Dependencies (2 minutes)

```bash
# Navigate to the project directory
cd nlq-app

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Key (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Start Backend Server (30 seconds)

```bash
cd backend/api
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Start Frontend (30 seconds)

Open a new terminal:

```bash
cd nlq-app/frontend/public
python -m http.server 3000
```

### 5. Open Browser (10 seconds)

Navigate to: **http://localhost:3000**

## First Query

### Connect to Database

1. Select database type (e.g., PostgreSQL)
2. Enter connection details:
   - Host: `localhost`
   - Port: `5432`
   - Database: `your_database`
   - User: `your_user`
   - Password: `your_password`
3. Click **Test Connection**

### Ask a Question

Try one of these examples:

```
What was our customer acquisition cost by channel last quarter?
```

```
Show me revenue by product category this year
```

```
What are our top 10 customers by total sales?
```

Click **Generate & Execute SQL** and watch the magic happen!

## What Happens Next?

1. ✨ AI converts your question to SQL
2. ✅ Query is validated for safety
3. 🚀 SQL executes against your database
4. 📊 Results display in a beautiful table
5. 📈 Export to CSV if needed

## Need Help?

### Common Issues

**Can't connect to database?**
- Check database is running
- Verify credentials
- Ensure database allows remote connections

**API key error?**
- Confirm `.env` file has `ANTHROPIC_API_KEY=your_key`
- No quotes around the key
- Restart backend server

**Frontend not loading?**
- Check both servers are running
- Try http://127.0.0.1:3000
- Clear browser cache

### Check Server Status

Backend: http://localhost:8000/health
API Docs: http://localhost:8000/docs

## Next Steps

1. **Explore Examples**: Click on example query chips in the UI
2. **View Documentation**: See README.md for full details
3. **Customize**: Modify system prompt for your use case
4. **Deploy**: Follow deployment guide for production use

## Sample Database Setup (Optional)

If you don't have a database ready, create a sample PostgreSQL database:

```sql
-- Create database
CREATE DATABASE analytics;

-- Connect to database
\c analytics

-- Create sample tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    acquisition_channel VARCHAR(50),
    created_date DATE,
    lifetime_value DECIMAL(10,2)
);

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product VARCHAR(100),
    amount DECIMAL(10,2),
    sale_date DATE
);

-- Insert sample data
INSERT INTO customers (name, acquisition_channel, created_date, lifetime_value) VALUES
('Acme Corp', 'Google Ads', '2024-01-15', 15000.00),
('TechStart Inc', 'Referral', '2024-02-20', 25000.00),
('Global Industries', 'LinkedIn', '2024-03-10', 45000.00);

INSERT INTO sales (customer_id, product, amount, sale_date) VALUES
(1, 'Product A', 5000.00, '2024-01-20'),
(1, 'Product B', 10000.00, '2024-02-15'),
(2, 'Product A', 12000.00, '2024-03-01'),
(2, 'Product C', 13000.00, '2024-03-15'),
(3, 'Product B', 20000.00, '2024-03-20'),
(3, 'Product C', 25000.00, '2024-04-10');
```

Now try asking:
- "What is the total sales by product?"
- "Which customer has the highest lifetime value?"
- "Show me sales by month"

## Performance Tips

- **Schema Caching**: Database schemas are cached for 1 hour
- **Row Limits**: Results automatically limited to 10,000 rows
- **Query Timeout**: 60-second default timeout
- **Concurrent Users**: Handles multiple users simultaneously

## Metrics to Track

Once you start using the system, monitor:
- **Query Count**: Shown in header
- **Avg Response Time**: Shown in header
- **Query Accuracy**: Track successful vs failed queries
- **User Adoption**: Number of active users

## Production Deployment

For production use:
1. Set `DEBUG=False` in `.env`
2. Use proper authentication
3. Set up HTTPS
4. Configure production database
5. Add monitoring and logging
6. See README.md for full deployment guide

## 2-Week Implementation Timeline

**Week 1: Setup & Configuration**
- Days 1-2: Environment setup and database connections
- Days 3-4: Customize system prompt for your domain
- Day 5: Internal testing with real queries

**Week 2: Deployment & Training**
- Days 6-7: Deploy to production environment
- Days 8-9: User training and documentation
- Day 10: Go live with monitoring

---

**Questions?** See README.md or check API docs at http://localhost:8000/docs
