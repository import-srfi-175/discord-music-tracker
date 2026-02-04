def format_number(num: int) -> str:
    """Formats a number with commas, e.g. 10,000"""
    return "{:,}".format(int(num))

def format_duration(ms: str | int) -> str:
    """Formats milliseconds to MM:SS"""
    try:
        seconds = int(ms) // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"
    except (ValueError, TypeError):
        return "0:00"
