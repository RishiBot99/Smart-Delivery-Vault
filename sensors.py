import board
import busio
import adafruit_bmp180 # Change to bmp180 if using the older model
import random

# Initialize I2C bus
try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_bmp180.Adafruit_BMP180_I2C(i2c)
    HARDWARE_CONNECTED = True
except Exception as e:
    print(f"⚠️ Hardware not detected, falling back to simulation: {e}")
    HARDWARE_CONNECTED = False

def get_sensor_data():
    """
    Returns: (temp, distance, tampered)
    Note: distance and tampered are kept for compatibility with app.py 
    but are hardcoded since we are only checking temperature.
    """
    
    if HARDWARE_CONNECTED:
        try:
            # REAL DATA from Raspberry Pi 5
            temp = round(sensor.temperature, 2)
        except Exception:
            temp = 0.0
    else:
        # SIMULATED DATA (If sensor is unplugged)
        temp = round(random.uniform(21.0, 23.5), 2)
    
    # Keeping these to prevent breaking app.py logic
    distance = 50 
    tampered = False
    
    return temp, distance, tampered