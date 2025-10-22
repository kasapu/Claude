"""
Natural Language to Multi-Platform SQL Query System
Generates optimized SQL for PostgreSQL, MySQL, Snowflake, and Databricks
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

from core.multi_platform_processor import MultiPlatformNLQProcessor
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NLQ Multi-Platform SQL Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    .platform-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    .badge-postgresql {
        background: #336791;
        color: white;
    }

    .badge-mysql {
        background: #00758F;
        color: white;
    }

    .badge-snowflake {
        background: #29B5E8;
        color: white;
    }

    .badge-databricks {
        background: #FF3621;
        color: white;
    }

    .complexity-low {
        color: #10b981;
        font-weight: 600;
    }

    .complexity-medium {
        color: #f59e0b;
        font-weight: 600;
    }

    .complexity-high {
        color: #ef4444;
        font-weight: 600;
    }

    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('ANTHROPIC_API_KEY', '')

# Sidebar
with st.sidebar:
    st.image("https://www.anthropic.com/images/icons/safari-pinned-tab.svg", width=50)
    st.title("⚙️ Settings")

    # API Key input
    api_key = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        help="Get your API key from https://console.anthropic.com/"
    )

    if api_key:
        st.session_state.api_key = api_key
        os.environ['ANTHROPIC_API_KEY'] = api_key

    st.divider()

    # Statistics
    st.subheader("📊 Statistics")
    st.metric("Total Queries", len(st.session_state.query_history))

    if st.session_state.query_history:
        st.metric("Last Query", st.session_state.query_history[-1]['timestamp'])

    st.divider()

    # Example queries
    st.subheader("💡 Example Questions")

    example_queries = [
        "What was our customer acquisition cost by channel last quarter?",
        "Show me total revenue by product category",
        "What are the top 10 customers by sales?",
        "Calculate average order value by region",
        "Show me monthly revenue trend for last year",
        "Which products have the highest profit margin?",
        "What is our customer retention rate?",
        "Show me sales by sales rep this quarter"
    ]

    for i, example in enumerate(example_queries[:5]):
        if st.button(f"📝 {example[:40]}...", key=f"example_{i}", use_container_width=True):
            st.session_state.example_query = example

    st.divider()

    # About
    st.subheader("ℹ️ About")
    st.markdown("""
    This tool generates optimized SQL queries for:
    - 🐘 **PostgreSQL**
    - 🐬 **MySQL**
    - ❄️ **Snowflake**
    - 🧱 **Databricks**

    Powered by Claude AI 🤖
    """)

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.query_history = []
        st.session_state.current_result = None
        st.rerun()

# Main content
st.markdown('<h1 class="main-header">🤖 Multi-Platform SQL Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transform your questions into optimized SQL for PostgreSQL, MySQL, Snowflake & Databricks</p>', unsafe_allow_html=True)

# Platform badges
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<span class="platform-badge badge-postgresql">PostgreSQL</span>', unsafe_allow_html=True)
with col2:
    st.markdown('<span class="platform-badge badge-mysql">MySQL</span>', unsafe_allow_html=True)
with col3:
    st.markdown('<span class="platform-badge badge-snowflake">Snowflake</span>', unsafe_allow_html=True)
with col4:
    st.markdown('<span class="platform-badge badge-databricks">Databricks</span>', unsafe_allow_html=True)

st.divider()

# Query input
st.subheader("💬 Ask Your Question")

# Check if example was clicked
default_query = st.session_state.get('example_query', '')
if default_query:
    user_query = st.text_area(
        "Enter your question in natural language:",
        value=default_query,
        height=100,
        placeholder="e.g., What was our customer acquisition cost by channel last quarter?",
        key="query_input"
    )
    # Clear the example after using it
    st.session_state.example_query = ''
else:
    user_query = st.text_area(
        "Enter your question in natural language:",
        height=100,
        placeholder="e.g., What was our customer acquisition cost by channel last quarter?",
        key="query_input"
    )

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    generate_button = st.button("🚀 Generate SQL for All Platforms", type="primary", use_container_width=True)

with col2:
    if st.session_state.current_result:
        compare_button = st.button("📊 Compare Platforms", use_container_width=True)
    else:
        compare_button = False

with col3:
    if st.session_state.current_result:
        download_button = st.button("💾 Download All", use_container_width=True)
    else:
        download_button = False

# Generate queries
if generate_button and user_query:
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar!")
    else:
        with st.spinner("🔄 Generating optimized SQL queries for all platforms..."):
            try:
                processor = MultiPlatformNLQProcessor(api_key=st.session_state.api_key)
                result = processor.compare_platforms(user_query)

                if result['success']:
                    st.session_state.current_result = result
                    st.session_state.query_history.append({
                        'query': user_query,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'platforms': len(result['queries'])
                    })
                    st.success("✅ SQL queries generated successfully for all platforms!")
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Display results
if st.session_state.current_result:
    result = st.session_state.current_result

    st.divider()
    st.subheader("📋 Generated SQL Queries")

    # Explanation
    if result.get('explanation'):
        st.markdown("### 📖 Explanation")
        st.info(result['explanation'])

    # Platform tabs
    tabs = st.tabs(["🐘 PostgreSQL", "🐬 MySQL", "❄️ Snowflake", "🧱 Databricks", "📊 Comparison"])

    platforms = ['postgresql', 'mysql', 'snowflake', 'databricks']

    # Individual platform tabs
    for i, (tab, platform_key) in enumerate(zip(tabs[:4], platforms)):
        with tab:
            if platform_key in result['queries']:
                query_data = result['queries'][platform_key]

                # Metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Platform", query_data['platform'])

                with col2:
                    complexity = query_data.get('complexity', 'Medium')
                    complexity_class = f"complexity-{complexity.lower()}"
                    st.markdown(f'**Complexity:** <span class="{complexity_class}">{complexity}</span>', unsafe_allow_html=True)

                with col3:
                    features = query_data.get('features_used', [])
                    st.metric("Features", len(features))

                # SQL Query
                st.markdown("#### 💻 SQL Query")
                st.code(query_data['sql'], language='sql', line_numbers=True)

                # Copy button
                if st.button(f"📋 Copy {query_data['platform']} SQL", key=f"copy_{platform_key}"):
                    st.toast(f"✅ {query_data['platform']} SQL copied to clipboard!")

                # Key Features
                if query_data.get('key_features'):
                    st.markdown("#### ✨ Key Features")
                    st.markdown(query_data['key_features'])

                # Features Used
                if features:
                    st.markdown("#### 🔧 SQL Features Used")
                    for feature in features:
                        st.markdown(f"- {feature}")
            else:
                st.warning(f"No query generated for {platform_key}")

    # Comparison tab
    with tabs[4]:
        st.markdown("### 🔍 Platform Comparison")

        # Create comparison table
        comparison_data = []

        for platform_key in platforms:
            if platform_key in result['queries']:
                query_data = result['queries'][platform_key]
                comparison_data.append({
                    'Platform': query_data['platform'],
                    'Complexity': query_data.get('complexity', 'N/A'),
                    'Features': ', '.join(query_data.get('features_used', [])),
                    'SQL Length': len(query_data['sql'])
                })

        if comparison_data:
            import pandas as pd
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Key Differences
        if result.get('key_differences'):
            st.markdown("### 🎯 Key Differences Between Platforms")
            st.markdown(result['key_differences'])

        # Side-by-side comparison
        st.markdown("### 📑 Side-by-Side SQL Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### PostgreSQL vs MySQL")
            subcol1, subcol2 = st.columns(2)

            with subcol1:
                st.markdown("**PostgreSQL**")
                if 'postgresql' in result['queries']:
                    st.code(result['queries']['postgresql']['sql'], language='sql')

            with subcol2:
                st.markdown("**MySQL**")
                if 'mysql' in result['queries']:
                    st.code(result['queries']['mysql']['sql'], language='sql')

        with col2:
            st.markdown("#### Snowflake vs Databricks")
            subcol1, subcol2 = st.columns(2)

            with subcol1:
                st.markdown("**Snowflake**")
                if 'snowflake' in result['queries']:
                    st.code(result['queries']['snowflake']['sql'], language='sql')

            with subcol2:
                st.markdown("**Databricks**")
                if 'databricks' in result['queries']:
                    st.code(result['queries']['databricks']['sql'], language='sql')

# Download all queries
if download_button and st.session_state.current_result:
    result = st.session_state.current_result

    # Create downloadable content
    download_content = f"""
# Multi-Platform SQL Queries
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Question: {result['original_query']}

## Explanation
{result.get('explanation', 'N/A')}

"""

    for platform_key in ['postgresql', 'mysql', 'snowflake', 'databricks']:
        if platform_key in result['queries']:
            query_data = result['queries'][platform_key]
            download_content += f"""
## {query_data['platform']}

```sql
{query_data['sql']}
```

**Complexity:** {query_data.get('complexity', 'N/A')}
**Features:** {', '.join(query_data.get('features_used', []))}

{query_data.get('key_features', '')}

---

"""

    download_content += f"""
## Key Differences
{result.get('key_differences', 'N/A')}
"""

    st.download_button(
        label="💾 Download All Queries as Markdown",
        data=download_content,
        file_name=f"sql_queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>🤖 Powered by Claude AI</strong> | Democratizing Data Access</p>
    <p>Generate optimized SQL for PostgreSQL, MySQL, Snowflake & Databricks instantly</p>
</div>
""", unsafe_allow_html=True)
