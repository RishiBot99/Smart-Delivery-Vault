import random
import time

# --- HARDWARE IMPORTS (Commented out for Laptop Demo) ---
# import board
# import adafruit_bmp180  # For Temperature
# import adafruit_vl53l0x # Common Lidar sensor library
# import geocoder         # For WiFi-based Geolocation: pip install geocoder

def get_sensor_data():
    """
    Returns: (temp, distance, tampered, location_str)
    """
    
    # ==========================================
    # MODE A: SIMULATED DATA (For Laptop Demo)
    # ==========================================
    temp = round(random.uniform(21.0, 23.5), 2)
    distance = 50.0 # cm
    tampered = False
    location = "34.0522° N, 118.2437° W (Simulated LA)" # Placeholder
    
    
    # ==========================================
    # MODE B: REAL RASPBERRY PI 5 (Commented Out)
    # ==========================================
    """
    # 1. Initialize I2C bus
    # i2c = board.I2C()
    
    # 2. Temperature (BMP180)
    # bmp180 = adafruit_bmp180.Adafruit_BMP180_I2C(i2c)
    # temp = bmp180.temperature
    
    # 3. Lidar (TF Mini LiDAR)
    # vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    # distance = vl53.range / 10 # convert mm to cm
    # if distance > 60 or distance < 40: # If box is opened/moved
    #     tampered = True
        
    # 4. WiFi Geolocation
    # g = geocoder.ip('me')
    # location = f"{g.latlng[0]}° N, {g.latlng[1]}° W (WiFi Geo)"
    """

    return temp, distance, tampered, location