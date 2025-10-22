import anthropic
import re
import os
from typing import Dict, Any
from pathlib import Path


class NLQProcessor:
    """Natural Language Query Processor using Claude AI"""

    def __init__(self, api_key: str = None):
        """
        Initialize NLQ Processor

        Args:
            api_key: Anthropic API key (if None, will use ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided or set in ANTHROPIC_API_KEY environment variable")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from file"""
        # Try to load from the root directory
        prompt_path = Path(__file__).parent.parent.parent / 'nlq-system-prompt.md'

        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                return f.read()
        else:
            # Fallback to a basic system prompt if file not found
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Default system prompt if file is not found"""
        return """You are an enterprise-grade Natural Language to SQL (NLQ) Query Assistant.

Your role is to convert plain English questions into accurate, optimized SQL queries.

Key responsibilities:
1. Parse natural language input to extract entities, metrics, filters, and time periods
2. Validate the question can be answered with available data
3. Generate optimized SQL queries with proper syntax for the target database
4. Provide clear explanations of the generated queries
5. Highlight any assumptions made

Always provide:
- The SQL query in a ```sql code block
- A plain-English explanation
- Any assumptions or limitations
- Estimated complexity (Low/Medium/High)

Ensure queries are:
- Syntactically correct for the target database platform
- Optimized for performance
- Safe (read-only, no destructive operations)
- Well-formatted and readable
"""

    def _format_schema(self, schema: Dict[str, Any]) -> str:
        """Format database schema for AI context"""
        schema_text = []

        for table_name, table_info in schema.items():
            schema_text.append(f"\nTable: {table_name}")
            schema_text.append("Columns:")

            for column in table_info.get('columns', []):
                col_desc = f"  - {column['name']} ({column['type']})"

                if column.get('primary_key'):
                    col_desc += " [PRIMARY KEY]"
                if column.get('foreign_key'):
                    col_desc += f" [FK -> {column['foreign_key']}]"
                if not column.get('nullable'):
                    col_desc += " [NOT NULL]"
                if column.get('description'):
                    col_desc += f" - {column['description']}"

                schema_text.append(col_desc)

        return "\n".join(schema_text)

    def process_query(self,
                     user_query: str,
                     db_schema: Dict[str, Any],
                     db_type: str) -> Dict[str, Any]:
        """
        Process natural language query and return SQL + metadata

        Args:
            user_query: Natural language question from user
            db_schema: Database schema dictionary
            db_type: Database type (POSTGRESQL, MYSQL, SNOWFLAKE, DATABRICKS)

        Returns:
            Dictionary containing:
            - sql: Generated SQL query
            - explanation: Plain-English explanation
            - assumptions: List of assumptions made
            - complexity: Estimated complexity (Low/Medium/High)
            - raw_response: Full AI response
        """
        # Build context
        context = f"""
Database Type: {db_type}

Available Schema:
{self._format_schema(db_schema)}

User Question: {user_query}

Please provide:
1. The optimized SQL query for {db_type}
2. Plain-English explanation of what the query does
3. Any assumptions you made
4. Estimated execution complexity (Low/Medium/High)
5. Expected result format

Format your response with clear sections.
"""

        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": context}
                ]
            )

            # Get response text
            response_text = message.content[0].text

            # Parse response
            return self._parse_response(response_text, user_query)

        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing query: {str(e)}",
                'sql': None,
                'explanation': None,
                'assumptions': [],
                'complexity': 'Unknown'
            }

    def _parse_response(self, response: str, original_query: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format

        Args:
            response: Raw response from Claude
            original_query: Original user question

        Returns:
            Structured dictionary with parsed components
        """
        # Extract SQL query (between ```sql and ```)
        sql_match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
        sql_query = sql_match.group(1).strip() if sql_match else ""

        # Extract explanation
        explanation = ""
        explanation_patterns = [
            r'\*\*Explanation\*\*:?\s*(.+?)(?:\n\n|\*\*|$)',
            r'Explanation:?\s*(.+?)(?:\n\n|\*\*|$)',
            r'Plain-English [Ee]xplanation:?\s*(.+?)(?:\n\n|\*\*|$)'
        ]

        for pattern in explanation_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                explanation = match.group(1).strip()
                break

        if not explanation:
            # Fallback: try to find any paragraph after the SQL
            parts = response.split('```')
            if len(parts) > 2:
                explanation = parts[2].strip().split('\n\n')[0] if parts[2].strip() else ""

        # Extract assumptions
        assumptions = []
        assumptions_match = re.search(r'\*\*Assumptions[:\s]+(.+?)(?:\n\n|\*\*|$)', response, re.DOTALL)
        if assumptions_match:
            assumptions_text = assumptions_match.group(1)
            assumptions = [line.strip('- ').strip() for line in assumptions_text.split('\n') if line.strip().startswith('-')]

        # Extract complexity
        complexity = "Medium"  # Default
        complexity_patterns = [
            r'\*\*Estimated Complexity\*\*:?\s*(Low|Medium|High)',
            r'Complexity:?\s*(Low|Medium|High)',
            r'\*\*Execution Complexity\*\*:?\s*(Low|Medium|High)'
        ]

        for pattern in complexity_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                complexity = match.group(1).capitalize()
                break

        return {
            'success': True,
            'sql': sql_query,
            'explanation': explanation,
            'assumptions': assumptions,
            'complexity': complexity,
            'original_query': original_query,
            'raw_response': response
        }

    def refine_query(self,
                    original_sql: str,
                    refinement_request: str,
                    db_type: str) -> Dict[str, Any]:
        """
        Refine an existing SQL query based on user feedback

        Args:
            original_sql: The original SQL query
            refinement_request: User's refinement request
            db_type: Database type

        Returns:
            Dictionary with refined SQL and explanation
        """
        context = f"""
Database Type: {db_type}

Original SQL Query:
```sql
{original_sql}
```

Refinement Request: {refinement_request}

Please provide the refined SQL query based on the user's request.
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": context}
                ]
            )

            response_text = message.content[0].text
            return self._parse_response(response_text, refinement_request)

        except Exception as e:
            return {
                'success': False,
                'error': f"Error refining query: {str(e)}",
                'sql': None
            }
