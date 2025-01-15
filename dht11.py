import dht11
import RPi.GPIO as GPIO
import time
# Set up the GPIO mode and pin
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
DHT_PIN = 4 # GPIO4, corresponding to physical pin 7 on the Raspberry Pi
# Create an instance of the dht11 class
sensor = dht11.DHT11(pin=DHT_PIN)
print("Starting DHT11 sensor reading...")
try:
 while True:
 # Read data from the sensor
 result = sensor.read()
 # If the read is successful, print temperature and humidity
 if result.is_valid():
 print(f"Temperature: {result.temperature}°C")
 print(f"Humidity: {result.humidity}%")
 else:
 print("Failed to retrieve data from sensor")
 # Wait before the next reading
 time.sleep(2)
except KeyboardInterrupt:
 print("Program exited.")
 GPIO.cleanup() # Clean up GPIO settings when the program ends
