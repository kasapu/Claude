# How to Run the NLQ Application on Your Machine

## Quick Start (5 Minutes)

### Step 1: Download the Code

If you have git:
```bash
git clone <your-repo-url>
cd nlq-app
```

Or download and extract the `nlq-app` folder to your computer.

### Step 2: Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key (starts with `sk-ant-`)
5. Copy the key

### Step 3: Set Up Environment

**On Mac/Linux:**
```bash
cd nlq-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
# Change: ANTHROPIC_API_KEY=your_anthropic_api_key_here
# To: ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

**On Windows:**
```cmd
cd nlq-app

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env with notepad
notepad .env
# Change: ANTHROPIC_API_KEY=your_anthropic_api_key_here
# To: ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### Step 4: Run the Application

**Option A: One-Command Startup (Recommended)**

Mac/Linux:
```bash
./start.sh
```

Windows:
```cmd
start.bat
```

**Option B: Manual Startup**

Terminal 1 (Backend):
```bash
cd backend/api
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend/public
python -m http.server 3000
```

### Step 5: Open Your Browser

Navigate to: **http://localhost:3000**

You should see the NLQ interface!

## Testing Without a Database

If you don't have a database ready, you can:

1. **Use a sample database** - See QUICKSTART.md for sample PostgreSQL setup
2. **Test the API** - Go to http://localhost:8000/docs to see the interactive API documentation
3. **Generate SQL only** - The system can generate SQL without executing it

## URLs You Can Access

Once running:

- **🌐 Main Application**: http://localhost:3000
- **🔌 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## Quick Database Test

If you have PostgreSQL installed locally:

```sql
-- Quick test database
CREATE DATABASE test_nlq;
\c test_nlq

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product VARCHAR(100),
    amount DECIMAL(10,2),
    sale_date DATE
);

INSERT INTO sales VALUES
(1, 'Product A', 100.00, '2024-01-15'),
(2, 'Product B', 150.00, '2024-01-20'),
(3, 'Product A', 200.00, '2024-02-10');
```

Then in the UI:
- Database: `postgresql`
- Host: `localhost`
- Port: `5432`
- Database: `test_nlq`
- User: `postgres` (or your username)
- Password: (your postgres password)

Ask: "What is the total sales by product?"

## Troubleshooting

**"Module not found" error?**
```bash
pip install -r requirements.txt
```

**"ANTHROPIC_API_KEY not set" error?**
- Make sure you created `.env` file
- Make sure you added your real API key
- Restart the backend server

**Can't connect to database?**
- Check database is running
- Verify connection credentials
- Make sure database allows local connections

**Port already in use?**
- Change port in .env file or start.sh
- Or kill existing process: `lsof -ti:8000 | xargs kill`

## What to Expect

1. **Connect to your database** using the form
2. **Ask questions in plain English** like:
   - "What was our revenue last quarter?"
   - "Show me top 10 customers"
   - "What's the average order value?"
3. **See the generated SQL** with explanation
4. **View results** in a table
5. **Export to CSV** if needed

## Screenshots

The UI includes:
- 🎯 Database connection panel
- 💬 Natural language query input
- 📊 Results table with export
- 💻 SQL code display
- 📈 Performance metrics

## Need Help?

- Check README.md for full documentation
- Visit http://localhost:8000/docs for API reference
- See example queries at http://localhost:8000/api/examples

---

**Ready to democratize data access!** 🚀
