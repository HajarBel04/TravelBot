def log_message(message):
    print(f"[LOG] {message}")

def validate_email_format(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_dates_from_string(date_string):
    from dateutil import parser
    try:
        return parser.parse(date_string)
    except ValueError:
        return None

def format_budget(budget):
    return f"${budget:,.2f}" if isinstance(budget, (int, float)) else None