#purely for test purposes w/o raspberry pi interface

import random

def get_sensor_data():
    """
    On your laptop: This generates fake data.
    On the Pi: Your partner will replace this with real BMP180/Lidar code.
    """
    # Simulate a steady temperature between 21 and 23 degrees
    temp = round(random.uniform(21.0, 23.5), 2)
    
    # Simulate a distance from Lidar (e.g., 50cm)
    distance = 50 
    
    # Simulate a tamper status
    tampered = False
    
    return temp, distance, tampered