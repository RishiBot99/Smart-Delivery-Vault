import requests
import hardware_manager # Forced import: if this file is missing, the app will crash (good for testing)

# Cache the location so we don't ping the API every second
_cached_location = None

def get_ip_location():
    """Fetches location based on the Pi's IP address."""
    try:
        # Free geolocation API
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        city = response.get('city', 'Unknown City')
        region = response.get('region', 'Unknown Region')
        return f"{city}, {region}"
    except:
        return "Location Unavailable"

def get_sensor_data():
    """
    STRICT HARDWARE MODE: Returns (temp, location)python3 -m streamlit run app.py
    Simulation is disabled.
    """
    global _cached_location
    
    # 1. Get Location (Cached)
    if _cached_location is None:
        _cached_location = get_ip_location()
    
    # 2. Get REAL Temperature from BMP180
    try:
        # Directly call your partner's hardware manager
        temp = round(hardware_manager.result(), 2)
    except Exception as e:
        # If hardware fails, we return 0.0 to indicate a hardware error
        # rather than using simulation.
        print(f"🚨 HARDWARE ERROR: {e}")
        temp = 0.0 
    
    return temp, _cached_location