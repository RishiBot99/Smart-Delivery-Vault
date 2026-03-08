import random
import requests

# Try to import your partner's hardware manager
try:
    import hardware_manager
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False

# Cache the location so we don't ping the API every second
_cached_location = None

def get_ip_location():
    """Fetches location based on the Pi's IP address."""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5).json()
        city = response.get('city', 'Unknown City')
        region = response.get('region', 'Unknown Region')
        return f"{city}, {region}"
    except:
        return "Location Unavailable"

def get_sensor_data():
    """
    Returns: (temp, location)
    """
    global _cached_location
    
    # 1. Get Location (only once per session)
    if _cached_location is None:
        _cached_location = get_ip_location()
    
    # 2. Get Temperature
    if HAS_HARDWARE:
        try:
            # Calls your partner's BMP180 code
            temp = round(hardware_manager.result(), 2)
        except:
            temp = round(random.uniform(22.0, 23.0), 2) # Hardware fallback
    else:
        # Laptop Simulation Mode
        temp = round(random.uniform(21.0, 23.5), 2)
    
    return temp, _cached_location