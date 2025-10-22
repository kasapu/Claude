from typing import Tuple, List


class QueryValidator:
    """SQL query validation and safety checks"""

    # Dangerous SQL operations to prevent
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER',
        'CREATE', 'INSERT', 'UPDATE', 'GRANT',
        'REVOKE', 'EXEC', 'EXECUTE'
    ]

    # Maximum number of rows to return
    MAX_ROWS = 10000

    @staticmethod
    def validate_safety(sql: str) -> Tuple[bool, str]:
        """
        Check if SQL query is safe (read-only)

        Args:
            sql: SQL query string

        Returns:
            Tuple of (is_safe, message)
        """
        sql_upper = sql.upper()

        # Check for dangerous keywords
        for keyword in QueryValidator.DANGEROUS_KEYWORDS:
            if f' {keyword} ' in f' {sql_upper} ':
                return False, f"Dangerous operation detected: {keyword}. Only SELECT queries are allowed."

        # Ensure query starts with SELECT (after comments and whitespace)
        cleaned_sql = sql_upper.strip()
        # Remove leading comments
        while cleaned_sql.startswith('--') or cleaned_sql.startswith('/*'):
            if cleaned_sql.startswith('--'):
                cleaned_sql = cleaned_sql.split('\n', 1)[1] if '\n' in cleaned_sql else ''
            elif cleaned_sql.startswith('/*'):
                end_comment = cleaned_sql.find('*/')
                if end_comment != -1:
                    cleaned_sql = cleaned_sql[end_comment + 2:]
                else:
                    return False, "Unclosed comment block"
            cleaned_sql = cleaned_sql.strip()

        if not cleaned_sql.startswith('SELECT') and not cleaned_sql.startswith('WITH'):
            return False, "Only SELECT queries (including CTEs with WITH) are allowed"

        return True, "Query passed safety checks"

    @staticmethod
    def enforce_row_limit(sql: str, max_rows: int = None) -> str:
        """
        Ensure query has a LIMIT clause

        Args:
            sql: SQL query string
            max_rows: Maximum rows to return (default: MAX_ROWS)

        Returns:
            SQL with LIMIT clause added or verified
        """
        if max_rows is None:
            max_rows = QueryValidator.MAX_ROWS

        sql_upper = sql.upper()

        # Check if LIMIT already exists
        if 'LIMIT' in sql_upper:
            # Extract existing limit value
            import re
            limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
            if limit_match:
                existing_limit = int(limit_match.group(1))
                if existing_limit > max_rows:
                    # Replace with max_rows
                    sql = re.sub(r'LIMIT\s+\d+', f'LIMIT {max_rows}', sql, flags=re.IGNORECASE)
            return sql

        # Add LIMIT clause
        return f"{sql.rstrip(';')} LIMIT {max_rows}"

    @staticmethod
    def validate_syntax_basic(sql: str) -> Tuple[bool, List[str]]:
        """
        Perform basic syntax validation

        Args:
            sql: SQL query string

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        # Check for balanced parentheses
        open_parens = sql.count('(')
        close_parens = sql.count(')')
        if open_parens != close_parens:
            warnings.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")

        # Check for balanced quotes
        single_quotes = sql.count("'") - sql.count("\\'")
        if single_quotes % 2 != 0:
            warnings.append("Unbalanced single quotes")

        double_quotes = sql.count('"') - sql.count('\\"')
        if double_quotes % 2 != 0:
            warnings.append("Unbalanced double quotes")

        # Check for common typos
        if ' form ' in sql.lower():
            warnings.append("Possible typo: 'form' instead of 'from'")

        if ' were ' in sql.lower() and ' where ' not in sql.lower():
            warnings.append("Possible typo: 'were' instead of 'where'")

        # Check for missing spaces around operators
        import re
        if re.search(r'[a-zA-Z0-9]=[a-zA-Z0-9]', sql):
            warnings.append("Missing spaces around '=' operator")

        is_valid = len(warnings) == 0
        return is_valid, warnings

    @staticmethod
    def estimate_complexity(sql: str) -> str:
        """
        Estimate query complexity based on structure

        Args:
            sql: SQL query string

        Returns:
            Complexity level: 'Low', 'Medium', or 'High'
        """
        sql_upper = sql.upper()

        # Count complexity indicators
        complexity_score = 0

        # JOINs
        join_count = sql_upper.count(' JOIN ')
        complexity_score += join_count * 2

        # Subqueries
        subquery_count = sql_upper.count('SELECT') - 1  # Subtract main query
        complexity_score += subquery_count * 3

        # CTEs (WITH clauses)
        cte_count = sql_upper.count(' WITH ')
        complexity_score += cte_count * 2

        # Window functions
        window_count = sql_upper.count(' OVER(')
        complexity_score += window_count * 2

        # Aggregations
        agg_functions = ['SUM(', 'AVG(', 'COUNT(', 'MIN(', 'MAX(']
        for func in agg_functions:
            complexity_score += sql_upper.count(func)

        # GROUP BY
        if ' GROUP BY ' in sql_upper:
            complexity_score += 1

        # ORDER BY
        if ' ORDER BY ' in sql_upper:
            complexity_score += 1

        # Determine complexity level
        if complexity_score <= 3:
            return 'Low'
        elif complexity_score <= 8:
            return 'Medium'
        else:
            return 'High'

    @staticmethod
    def get_query_type(sql: str) -> str:
        """
        Determine the type of SQL query

        Args:
            sql: SQL query string

        Returns:
            Query type: 'SELECT', 'INSERT', 'UPDATE', 'DELETE', etc.
        """
        sql_upper = sql.strip().upper()

        # Remove leading comments
        while sql_upper.startswith('--') or sql_upper.startswith('/*'):
            if sql_upper.startswith('--'):
                sql_upper = sql_upper.split('\n', 1)[1] if '\n' in sql_upper else ''
            elif sql_upper.startswith('/*'):
                end_comment = sql_upper.find('*/')
                if end_comment != -1:
                    sql_upper = sql_upper[end_comment + 2:]
            sql_upper = sql_upper.strip()

        # Determine query type
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('WITH'):
            return 'SELECT'  # CTE queries are essentially SELECT
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        elif sql_upper.startswith('CREATE'):
            return 'CREATE'
        elif sql_upper.startswith('DROP'):
            return 'DROP'
        elif sql_upper.startswith('ALTER'):
            return 'ALTER'
        else:
            return 'UNKNOWN'
