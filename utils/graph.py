from datetime import datetime

def create_timeline_url(data: list[dict], title: str = "Listening History") -> str:
    """
    Generates a QuickChart URL for a line chart.
    data: list of dicts with 'name' (track/artist) and 'date' (timestamp).
    This mimics a simple activity timeline.
    
    Since managing exact timestamps for a timeline is complex with just a list of tracks, 
    we will aggregate by day or similar if possible. 
    However, for simplicity given minimal dependencies, we will just plot the available data points if they have counts,
    OR if this is from 'weeklytrackchart', we might have play counts per day?
    
    If data is just a list of tracks with timestamps, we can bucket them.
    Let's assume data is a list of objects with a 'date' field (unix timestamp or struct).
    """
    # Simply return a placeholder chart for now if data processing is too complex for a "minimal" implementation without pandas.
    # But let's try a simple bucket by day.
    
    dates = []
    for item in data:
        dt = item.get("date", {}).get("#text") # Last.fm often returns string dates
        if dt:
            # Parse "3 Feb 2025, 10:00"
            try:
                d = datetime.strptime(dt, "%d %b %Y, %H:%M") # Approx format
                dates.append(d.strftime("%Y-%m-%d"))
            except:
                pass
    
    if not dates:
        return None
        
    # Count occurrences per day
    counts = {}
    for d in dates:
        counts[d] = counts.get(d, 0) + 1
        
    sorted_dates = sorted(counts.keys())
    data_points = [counts[d] for d in sorted_dates]
    
    # Construct QuickChart URL
    base_url = "https://quickchart.io/chart?c="
    chart_config = {
        "type": "line",
        "data": {
            "labels": sorted_dates,
            "datasets": [{
                "label": "Scrobbles",
                "data": data_points,
                "borderColor": "#ba0000",
                "fill": False
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": title
            }
        }
    }
    
    import json
    import urllib.parse
    
    # Minimal URL encoding
    json_str = json.dumps(chart_config)
    encoded = urllib.parse.quote(json_str)
    return base_url + encoded
