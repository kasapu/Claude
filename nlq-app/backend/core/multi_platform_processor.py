import anthropic
import os
from typing import Dict, Any, List
from pathlib import Path


class MultiPlatformNLQProcessor:
    """
    Enhanced NLQ Processor that generates SQL for all database platforms simultaneously
    """

    def __init__(self, api_key: str = None):
        """Initialize with Anthropic API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.platforms = ['PostgreSQL', 'MySQL', 'Snowflake', 'Databricks']
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load or create system prompt"""
        prompt_path = Path(__file__).parent.parent / 'nlq-system-prompt.md'

        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                return f.read()

        return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Default system prompt for multi-platform SQL generation"""
        return """You are an expert SQL query generator for multiple database platforms.

When given a natural language question, you must generate optimized SQL queries for ALL of these platforms:
1. PostgreSQL
2. MySQL
3. Snowflake
4. Databricks (Spark SQL)

For each platform, provide:
- Optimized SQL query using platform-specific syntax and functions
- Key differences from standard SQL
- Platform-specific optimizations

Format your response as follows:

## PostgreSQL
```sql
[PostgreSQL-specific SQL]
```
**Key Features:** [Highlight PostgreSQL-specific syntax/functions used]

## MySQL
```sql
[MySQL-specific SQL]
```
**Key Features:** [Highlight MySQL-specific syntax/functions used]

## Snowflake
```sql
[Snowflake-specific SQL]
```
**Key Features:** [Highlight Snowflake-specific syntax/functions used]

## Databricks
```sql
[Databricks-specific SQL]
```
**Key Features:** [Highlight Databricks-specific syntax/functions used]

## Explanation
[Plain-English explanation of what all queries do]

## Key Differences
[Explain main syntax/functional differences between platforms]

Always use best practices and platform-specific optimizations."""

    def generate_multi_platform_sql(self,
                                    user_query: str,
                                    db_schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate SQL queries for all database platforms simultaneously

        Args:
            user_query: Natural language question
            db_schema: Optional database schema for context

        Returns:
            Dictionary with SQL for each platform plus metadata
        """

        # Build context
        context = f"""
User Question: {user_query}

Generate optimized SQL queries for this question for ALL four database platforms:
- PostgreSQL
- MySQL
- Snowflake
- Databricks (Spark SQL)

"""

        if db_schema:
            context += f"\nAvailable Schema:\n{self._format_schema(db_schema)}\n"

        context += """
Provide the SQL query for each platform, highlighting platform-specific features and optimizations.
"""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8192,  # Increased for multiple queries
                system=self.system_prompt,
                messages=[{"role": "user", "content": context}]
            )

            response_text = message.content[0].text

            # Parse response
            return self._parse_multi_platform_response(response_text, user_query)

        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating queries: {str(e)}",
                'queries': {}
            }

    def _parse_multi_platform_response(self, response: str, original_query: str) -> Dict[str, Any]:
        """Parse AI response to extract SQL for each platform"""
        import re

        result = {
            'success': True,
            'original_query': original_query,
            'queries': {},
            'explanation': '',
            'key_differences': '',
            'raw_response': response
        }

        # Extract SQL for each platform
        platforms = {
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'snowflake': 'Snowflake',
            'databricks': 'Databricks'
        }

        for platform_key, platform_name in platforms.items():
            # Pattern to match SQL code blocks for each platform
            pattern = rf'##\s*{platform_name}.*?```sql\n(.*?)\n```'
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)

            if match:
                sql = match.group(1).strip()

                # Extract key features for this platform
                features_pattern = rf'##\s*{platform_name}.*?```sql.*?```\s*\*\*Key Features:\*\*\s*(.*?)(?=##|\Z)'
                features_match = re.search(features_pattern, response, re.DOTALL | re.IGNORECASE)
                features = features_match.group(1).strip() if features_match else ""

                result['queries'][platform_key] = {
                    'sql': sql,
                    'platform': platform_name,
                    'key_features': features
                }

        # Extract general explanation
        explanation_pattern = r'##\s*Explanation\s*(.*?)(?=##|\Z)'
        explanation_match = re.search(explanation_pattern, response, re.DOTALL | re.IGNORECASE)
        if explanation_match:
            result['explanation'] = explanation_match.group(1).strip()

        # Extract key differences
        differences_pattern = r'##\s*Key Differences\s*(.*?)(?=##|\Z)'
        differences_match = re.search(differences_pattern, response, re.DOTALL | re.IGNORECASE)
        if differences_match:
            result['key_differences'] = differences_match.group(1).strip()

        return result

    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """Format database schema for context"""
        schema_text = []

        for table_name, table_info in schema.items():
            schema_text.append(f"\nTable: {table_name}")
            schema_text.append("Columns:")

            for column in table_info.get('columns', []):
                col_desc = f"  - {column['name']} ({column['type']})"
                if column.get('primary_key'):
                    col_desc += " [PK]"
                if column.get('foreign_key'):
                    col_desc += f" [FK -> {column['foreign_key']}]"
                schema_text.append(col_desc)

        return "\n".join(schema_text)

    def compare_platforms(self, user_query: str) -> Dict[str, Any]:
        """
        Generate queries and provide detailed platform comparison

        Args:
            user_query: Natural language question

        Returns:
            Comprehensive comparison across platforms
        """
        result = self.generate_multi_platform_sql(user_query)

        if not result['success']:
            return result

        # Add complexity analysis for each platform
        for platform_key, query_data in result['queries'].items():
            sql = query_data['sql']
            query_data['complexity'] = self._estimate_complexity(sql)
            query_data['features_used'] = self._identify_features(sql, platform_key)

        return result

    def _estimate_complexity(self, sql: str) -> str:
        """Estimate query complexity"""
        sql_upper = sql.upper()
        score = 0

        # Count complexity indicators
        score += sql_upper.count(' JOIN ') * 2
        score += (sql_upper.count('SELECT') - 1) * 3  # Subqueries
        score += sql_upper.count(' WITH ') * 2
        score += sql_upper.count(' OVER(') * 2
        score += sql_upper.count('GROUP BY')
        score += sql_upper.count('WINDOW')

        if score <= 3:
            return 'Low'
        elif score <= 8:
            return 'Medium'
        else:
            return 'High'

    def _identify_features(self, sql: str, platform: str) -> List[str]:
        """Identify SQL features used"""
        sql_upper = sql.upper()
        features = []

        if 'JOIN' in sql_upper:
            features.append('Joins')
        if 'GROUP BY' in sql_upper:
            features.append('Aggregation')
        if 'OVER(' in sql_upper or 'WINDOW' in sql_upper:
            features.append('Window Functions')
        if sql_upper.count('SELECT') > 1:
            features.append('Subqueries')
        if 'WITH' in sql_upper:
            features.append('CTEs')
        if 'CASE' in sql_upper:
            features.append('Conditional Logic')

        # Platform-specific features
        if platform == 'postgresql':
            if 'INTERVAL' in sql_upper:
                features.append('Date Intervals')
            if '::' in sql:
                features.append('Type Casting')
        elif platform == 'snowflake':
            if 'QUALIFY' in sql_upper:
                features.append('QUALIFY Clause')
            if 'DATEADD' in sql_upper or 'DATEDIFF' in sql_upper:
                features.append('Date Functions')
        elif platform == 'databricks':
            if 'DELTA' in sql_upper:
                features.append('Delta Lake')

        return features
