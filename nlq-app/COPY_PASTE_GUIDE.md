# 📋 Copy-Paste Guide to Run NLQ System

## ⚡ Fastest Way to Run (Copy & Paste Each Block)

### 1️⃣ Prerequisites Check

Open your terminal and verify you have Python:
```bash
python3 --version  # Should show Python 3.8 or higher
```

If you don't have Python, download from: https://www.python.org/downloads/

### 2️⃣ Navigate to the Project

```bash
cd nlq-app
```

### 3️⃣ Set Up Virtual Environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 4️⃣ Install Dependencies (One Command)

```bash
pip install fastapi uvicorn pydantic psycopg2-binary mysql-connector-python snowflake-connector-python databricks-sql-connector anthropic python-dotenv python-multipart requests
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

### 5️⃣ Create .env File

**Mac/Linux:**
```bash
cat > .env << 'EOF'
ANTHROPIC_API_KEY=PASTE_YOUR_KEY_HERE
HOST=0.0.0.0
PORT=8000
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_QUERY_ROWS=10000
QUERY_TIMEOUT=60
SCHEMA_CACHE_TTL=3600
LOG_LEVEL=INFO
EOF
```

**Windows (PowerShell):**
```powershell
@"
ANTHROPIC_API_KEY=PASTE_YOUR_KEY_HERE
HOST=0.0.0.0
PORT=8000
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
MAX_QUERY_ROWS=10000
QUERY_TIMEOUT=60
SCHEMA_CACHE_TTL=3600
LOG_LEVEL=INFO
"@ | Out-File -Encoding ASCII .env
```

**Or manually:**
```bash
cp .env.example .env
# Then edit .env with your text editor and replace PASTE_YOUR_KEY_HERE
```

🔑 **Get Your API Key**: https://console.anthropic.com/settings/keys

### 6️⃣ Start Backend Server

```bash
cd backend/api
python main.py
```

You should see:
```
🚀 NLQ System Backend Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All checks passed!
🔵 Starting server...

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this terminal running!**

### 7️⃣ Start Frontend (New Terminal)

Open a **NEW** terminal window:

```bash
cd nlq-app/frontend/public
python3 -m http.server 3000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
```

### 8️⃣ Open in Browser

Click or copy this URL: **http://localhost:3000**

---

## 🎯 What You'll See

### Landing Page:
```
┌─────────────────────────────────────────────────┐
│  🤖 Natural Language Query                      │
│  Transform your questions into SQL queries      │
│                                    Queries: 0   │
│                                    Avg Time: 0s │
└─────────────────────────────────────────────────┘

📊 Database Connection
┌─────────────────────────────────────────────────┐
│ Database Type: [PostgreSQL ▼]                  │
│ Host: [localhost]        Port: [5432]          │
│ Database: [analytics]    User: [analyst]       │
│ Password: [••••••••]                           │
│ [Test Connection]                               │
└─────────────────────────────────────────────────┘

💬 Ask Your Question
┌─────────────────────────────────────────────────┐
│ What was our customer acquisition cost by       │
│ channel last quarter?                           │
│                                                 │
│ [🚀 Generate & Execute SQL] [📝 Generate Only] │
└─────────────────────────────────────────────────┘
```

---

## 🧪 Quick Test Without Database

You can test the system without a database:

1. **Skip** the database connection section
2. **Type** a question: "Show me total sales by product"
3. **Click** "Generate SQL Only"
4. You'll see the generated SQL even without executing it!

---

## 🗄️ Quick PostgreSQL Test Database

If you have PostgreSQL installed:

```sql
-- Create test database
CREATE DATABASE nlq_test;

-- Connect
\c nlq_test

-- Create table
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product VARCHAR(100),
    region VARCHAR(50),
    amount DECIMAL(10,2),
    sale_date DATE
);

-- Insert sample data
INSERT INTO sales (product, region, amount, sale_date) VALUES
('Widget A', 'North', 1500.00, '2024-01-15'),
('Widget B', 'South', 2300.00, '2024-01-20'),
('Widget A', 'East', 1800.00, '2024-02-10'),
('Widget C', 'West', 3200.00, '2024-02-15'),
('Widget B', 'North', 2100.00, '2024-03-05'),
('Widget A', 'South', 1950.00, '2024-03-12');
```

**Then in the UI:**
- Database Type: `PostgreSQL`
- Host: `localhost`
- Port: `5432`
- Database: `nlq_test`
- User: `postgres` (or your username)
- Password: (your password)

**Try these questions:**
```
"What is the total sales amount by product?"
"Show me sales by region"
"What were our sales in February 2024?"
"Which product had the highest sales?"
```

---

## 🌐 Access Points

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| 🎨 **Web UI** | http://localhost:3000 | Main application interface |
| 🔌 **API** | http://localhost:8000 | Backend REST API |
| 📚 **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| ❤️ **Health** | http://localhost:8000/health | Server health check |
| 📝 **Examples** | http://localhost:8000/api/examples | Example queries |

---

## 🛑 Stop the Servers

Press `Ctrl+C` in each terminal window to stop the servers.

---

## 🆘 Troubleshooting

### "pip: command not found"
Try `pip3` instead of `pip`

### "Port already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in .env
PORT=8001
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Cannot connect to database"
- Verify database is running: `psql -l` (for PostgreSQL)
- Check credentials are correct
- Ensure database allows localhost connections

### "ANTHROPIC_API_KEY not set"
1. Check `.env` file exists in `nlq-app/` directory
2. Verify you added your real API key (starts with `sk-ant-`)
3. No quotes around the key
4. Restart backend server

---

## 📸 Expected Behavior

### ✅ Successful Query:
1. Green "Connected" status
2. Generated SQL appears in code block
3. Plain-English explanation
4. Data table with results
5. "Export CSV" button enabled

### ❌ If Query Fails:
- Red error message appears
- Check database connection
- Verify table/column names exist
- Review SQL in the error message

---

## 🎓 Example Questions to Try

**Customer Analytics:**
- "What was our customer acquisition cost by channel last quarter?"
- "Show me new customer growth by month"

**Sales Performance:**
- "What is total revenue by product category?"
- "Show me top 10 customers by sales"

**Financial:**
- "What are our largest expense categories?"
- "Show me profit margin by product"

**Operations:**
- "What's the average order fulfillment time?"
- "Which warehouse has the most inventory?"

---

## 🚀 You're Ready!

The system is now running. Go to **http://localhost:3000** and start asking questions!

**Need more help?** Check:
- `README.md` - Full documentation
- `QUICKSTART.md` - 5-minute guide
- http://localhost:8000/docs - API reference
