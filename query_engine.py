"""
Query engine that translates natural language questions into pandas operations,
executes real code, and returns verified answers.
"""

import os
import re
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic
from prompts import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic()


def load_data():
    """Load and prepare the consolidated financial data."""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "consolidated_master.csv"))
    df['Date'] = pd.to_datetime(df['Date'])
    return df


# Global dataframe - loaded once
df = load_data()


def get_data_summary():
    """Generate a quick summary of the current data for context."""
    total_revenue = df[df['Type'] == 'Revenue']['Amount'].sum()
    total_expenses = df[df['Type'] == 'Expense']['Amount'].sum()
    date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
    
    summary = f"""
CURRENT DATA SNAPSHOT:
- Total Revenue: ${total_revenue:,.2f}
- Total Expenses: ${total_expenses:,.2f}
- Net Income: ${total_revenue - total_expenses:,.2f}
- Transaction Count: {len(df):,}
- Date Range: {date_range}
- Departments: {', '.join(df['Department'].unique())}
"""
    return summary


def extract_code(response_text: str) -> str:
    """Extract pandas code from between <code> tags."""
    pattern = r'<code>(.*?)</code>'
    match = re.search(pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def execute_code(code: str, dataframe: pd.DataFrame) -> dict:
    """
    Safely execute pandas code and return the result.
    Returns dict with 'success', 'result', and 'error' keys.
    """
    # Create a restricted namespace for execution
    namespace = {
        'df': dataframe,
        'pd': pd,
        'result': None
    }
    
    try:
        exec(code, namespace)
        return {
            'success': True,
            'result': namespace.get('result', 'Code executed but no result was set.'),
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'result': None,
            'error': str(e)
        }


def ask_financial_question(question: str) -> dict:
    """
    Send a natural language question to Claude, get pandas code,
    execute it, and return the verified result.
    
    Returns dict with:
        - answer: The actual computed answer
        - code: The pandas code that generated it
        - explanation: Claude's explanation of the code
        - success: Whether execution worked
        - error: Error message if execution failed
    """
    # Build the prompt with data context
    data_context = get_data_summary()
    
    full_prompt = f"""{data_context}

USER QUESTION: {question}

Write pandas code to answer this question. Remember to store your final answer in the `result` variable."""

    # Call Claude API to get the code
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )
    
    response_text = response.content[0].text
    
    # Extract the code
    code = extract_code(response_text)
    
    if not code:
        return {
            'answer': "I couldn't generate code to answer that question.",
            'code': None,
            'explanation': response_text,
            'success': False,
            'error': 'No code block found in response'
        }
    
    # Extract explanation (everything after the </code> tag)
    explanation = response_text.split('</code>')[-1].strip() if '</code>' in response_text else ''
    
    # Execute the code
    execution_result = execute_code(code, df)
    
    if execution_result['success']:
        return {
            'answer': execution_result['result'],
            'code': code,
            'explanation': explanation,
            'success': True,
            'error': None
        }
    else:
        return {
            'answer': f"I wrote code but it had an error: {execution_result['error']}",
            'code': code,
            'explanation': explanation,
            'success': False,
            'error': execution_result['error']
        }


# Test it standalone
if __name__ == "__main__":
    print("=" * 60)
    print("FINANCIAL DATA AI ASSISTANT - REAL CODE EXECUTION TEST")
    print("=" * 60)
    print(get_data_summary())
    
    # Test questions
    test_questions = [
        "What was total revenue for the year?",
        "What were Marketing expenses in Q1?",
        "Which department had the highest expenses?"
    ]
    
    for question in test_questions:
        print("=" * 60)
        print(f"QUESTION: {question}")
        print("-" * 60)
        
        result = ask_financial_question(question)
        
        print(f"ANSWER: {result['answer']}")
        print(f"\nCODE EXECUTED:")
        print(result['code'])
        print(f"\nSUCCESS: {result['success']}")
        if result['error']:
            print(f"ERROR: {result['error']}")
        print()