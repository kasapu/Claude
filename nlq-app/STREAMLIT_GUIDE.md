# 🎯 Multi-Platform SQL Generator - Streamlit Edition

> Generate optimized SQL queries for PostgreSQL, MySQL, Snowflake, and Databricks simultaneously!

## ✨ What's New

This enhanced version generates SQL for **ALL 4 database platforms at once** from a single natural language question:

- 🐘 **PostgreSQL** - Open-source relational database
- 🐬 **MySQL** - Popular relational database
- ❄️ **Snowflake** - Cloud data warehouse
- 🧱 **Databricks** - Unified analytics platform

### Key Features

✅ **Multi-Platform Generation** - Get 4 SQL queries instantly
✅ **Platform Comparison** - See differences side-by-side
✅ **Syntax Highlighting** - Beautiful code display
✅ **Feature Detection** - Identifies SQL features used
✅ **Complexity Analysis** - Estimates query complexity
✅ **Download All** - Export all queries as Markdown
✅ **Query History** - Track all your questions
✅ **Example Library** - Pre-built example queries

## 🚀 Quick Start (2 Minutes!)

### Step 1: Install Dependencies

```bash
cd nlq-app
pip install streamlit pandas anthropic python-dotenv
```

### Step 2: Set Your API Key

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

Get your API key: https://console.anthropic.com/settings/keys

### Step 3: Run Streamlit

```bash
streamlit run streamlit_app.py
```

Or use the startup script:

```bash
./run_streamlit.sh  # Mac/Linux
# OR
run_streamlit.bat   # Windows
```

### Step 4: Open Browser

Streamlit will automatically open your browser to:
**http://localhost:8501**

## 🎨 User Interface

### Main Features

1. **Question Input** - Type your question in plain English
2. **Platform Tabs** - View each platform's SQL separately
3. **Comparison View** - Side-by-side comparison
4. **Metrics** - Complexity, features, and statistics
5. **Download** - Export all queries
6. **History** - Track past queries

### Sidebar

- 🔑 **API Key Input** - Enter your Anthropic API key
- 📊 **Statistics** - Total queries and timestamp
- 💡 **Example Questions** - Click to try
- 🗑️ **Clear History** - Reset everything

## 💬 Example Questions

Try these to see the multi-platform magic:

### Customer Analytics
```
What was our customer acquisition cost by channel last quarter?
```

### Revenue Analysis
```
Show me total revenue by product category for this year
```

### Sales Performance
```
What are the top 10 customers by total sales?
```

### Financial Metrics
```
Calculate average order value by region and month
```

### Trend Analysis
```
Show me monthly revenue trend for the last 12 months
```

### Complex Queries
```
What is our customer retention rate by cohort with year-over-year comparison?
```

## 📊 What You'll See

For each platform, you get:

1. **Optimized SQL Query** - Platform-specific syntax
2. **Complexity Rating** - Low/Medium/High
3. **Features Used** - List of SQL features (JOINs, CTEs, etc.)
4. **Key Features** - Platform-specific optimizations
5. **Code Highlighting** - Syntax-colored SQL

### Comparison Tab

- **Platform Comparison Table** - Side-by-side metrics
- **Key Differences** - Explanation of variations
- **Split View** - PostgreSQL vs MySQL and Snowflake vs Databricks

## 🔍 Platform-Specific Features

### PostgreSQL
- `INTERVAL` for date arithmetic
- `::` type casting
- Advanced JSON support
- Window functions with `FILTER`

### MySQL
- Backtick identifiers
- `DATE_ADD`/`DATE_SUB` functions
- `LIMIT` syntax
- Storage engine optimizations

### Snowflake
- `DATEADD`/`DATEDIFF` functions
- `QUALIFY` clause for window functions
- `$$` identifier quoting
- `VARIANT` for JSON data

### Databricks
- Delta Lake syntax
- Spark SQL optimizations
- `backtick` identifiers
- Complex data types (arrays, structs)

## 📥 Download Queries

Click "💾 Download All" to get a Markdown file containing:

- All 4 SQL queries
- Explanations
- Key features for each platform
- Complexity analysis
- Key differences summary

Perfect for documentation or sharing with your team!

## 🎯 Use Cases

### For Analysts
- Generate queries without knowing SQL
- Compare syntax across platforms
- Learn platform-specific features

### For Developers
- Quick query prototyping
- Multi-platform compatibility testing
- Best practices reference

### For Data Engineers
- Migration planning between platforms
- Query optimization comparison
- Training material for teams

### For Business Users
- Self-service data access
- No SQL knowledge required
- Instant query generation

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```env
ANTHROPIC_API_KEY=your_key_here
```

### Streamlit Configuration (Optional)

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#667eea"
backgroundColor="#ffffff"
secondaryBackgroundColor="#f0f2f6"
textColor="#262730"

[server]
port=8501
headless=false
```

## 🔧 Advanced Features

### Query History

- Automatically tracks all questions
- Shows timestamp and platform count
- Clear history with one click

### Example Library

Pre-built questions covering:
- Customer analytics
- Revenue analysis
- Sales performance
- Financial metrics
- Operational efficiency

### Platform Badges

Color-coded badges for each database:
- 🟦 PostgreSQL (Blue)
- 🟩 MySQL (Teal)
- 🟦 Snowflake (Light Blue)
- 🟥 Databricks (Red)

## 📊 Metrics Displayed

For each query:
- **Platform Name**
- **Complexity** (Low/Medium/High)
- **Feature Count** (Number of SQL features used)
- **SQL Length** (Characters)
- **Features Used** (JOINs, CTEs, Window Functions, etc.)

## 🆚 Comparison Features

### Side-by-Side View
- PostgreSQL vs MySQL
- Snowflake vs Databricks
- Highlight syntax differences

### Comparison Table
Platform | Complexity | Features | SQL Length
---------|-----------|----------|------------
PostgreSQL | Medium | CTEs, JOINs | 245
MySQL | Low | JOINs | 198
Snowflake | Medium | Window, QUALIFY | 267
Databricks | Medium | Delta, Window | 289

## 💡 Tips for Best Results

1. **Be Specific** - Include time periods, dimensions, and metrics
2. **Use Business Terms** - "revenue", "customers", not table names
3. **Provide Context** - "last quarter", "by region", etc.
4. **Complex is OK** - System handles multi-step queries

### Good Examples
✅ "What was revenue by product category in Q4 2024?"
✅ "Show me top 10 customers by lifetime value"
✅ "Calculate month-over-month growth for last year"

### Too Vague
❌ "Show me data"
❌ "Get sales"
❌ "List everything"

## 🐛 Troubleshooting

### "No module named 'streamlit'"
```bash
pip install streamlit
```

### "API key not set"
- Add key to `.env` file
- OR enter in sidebar
- Restart Streamlit

### "Port already in use"
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Queries not generating
- Check API key is valid
- Verify internet connection
- Check Anthropic service status

## 📱 Mobile Support

Streamlit is mobile-responsive! Access from:
- 📱 Phone browsers
- 💻 Tablets
- 🖥️ Desktop

## 🚀 Deployment Options

### Local (Development)
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud (Free!)
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect repository
4. Deploy!

Get a public URL like: `https://yourapp.streamlit.app`

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

```bash
docker build -t nlq-streamlit .
docker run -p 8501:8501 nlq-streamlit
```

### Heroku, AWS, Azure, GCP
See Streamlit deployment docs: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app

## 🎓 Learning Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **SQL Tutorial**: Compare syntax across platforms
- **Platform Docs**:
  - PostgreSQL: https://www.postgresql.org/docs/
  - MySQL: https://dev.mysql.com/doc/
  - Snowflake: https://docs.snowflake.com/
  - Databricks: https://docs.databricks.com/

## 📊 Performance

- **Query Generation**: 2-5 seconds
- **UI Response**: Instant
- **Concurrent Users**: Unlimited (depends on hosting)
- **Cache**: Results cached in session

## 🔒 Security

- API keys stored securely in `.env`
- Session-based authentication
- No data persistence by default
- HTTPS recommended for production

## 🤝 Support

### Common Issues

**Platform missing from results?**
- Check API response in console
- Verify question is clear
- Try rephrasing

**Slow generation?**
- First query may be slower
- Check internet connection
- Anthropic API rate limits

**UI not updating?**
- Refresh browser
- Clear Streamlit cache
- Restart app

## 📈 Future Enhancements

Planned features:
- [ ] Schema integration for context
- [ ] Query execution against live databases
- [ ] Results visualization
- [ ] Query optimization suggestions
- [ ] Export to different formats (CSV, JSON)
- [ ] Collaborative features
- [ ] Query templates library

## 🎉 You're Ready!

Run the app and start generating multi-platform SQL queries instantly!

```bash
./run_streamlit.sh
```

Then go to: **http://localhost:8501**

---

**Built with ❤️ using Claude AI and Streamlit**

Democratizing data access across all major database platforms! 🚀
