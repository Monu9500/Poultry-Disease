import time
import spidev
import math
import serial
import RPi.GPIO as GPIO
import dht11

# SPI setup for MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device 0
spi.max_speed_hz = 1350000  # Set SPI speed

# Define MQ-135 pin on MCP3008
MQ135_CHANNEL = 0  

# Constants for MQ-135 Calibration
RLOAD = 10.0  # Load resistance in kilo-ohms
RO_CLEAN_AIR_FACTOR = 3.6  # Ro in clean air / Rs
BASE_AMMONIA_PPM = 25  # Normal room level of ammonia in ppm

# Set up pH sensor serial connection
ser = serial.Serial(
    port='/dev/ttyAMA0',  # Replace with your serial port
    baudrate=9600,      # Adjust baudrate as per your sensor's specifications
    timeout=1           # Set a timeout for reading
)

# Set up the GPIO mode and pin for DHT11
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
DHT_PIN = 17  # GPIO17, physical pin 11 on the Raspberry Pi
sensor = dht11.DHT11(pin=DHT_PIN)

# Function to read SPI data from MCP3008
def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((adc[1] & 3) << 8) + adc[2]
    return value

# Function to calculate sensor resistance (Rs)
def get_resistance(adc_value):
    if adc_value == 0:
        return float('inf')  # Avoid division by zero
    return (1023.0 / adc_value - 1.0) * RLOAD

# Function to calibrate MQ-135 (Get Ro in fresh air)
def calibrate_sensor():
    print("Calibrating MQ-135 sensor, please wait...")
    readings = []
    for _ in range(100):  # Take 100 samples for accuracy
        adc_value = read_adc(MQ135_CHANNEL)
        rs = get_resistance(adc_value)
        readings.append(rs)
        time.sleep(0.1)
    avg_rs = sum(readings) / len(readings)
    ro = avg_rs / RO_CLEAN_AIR_FACTOR  # Calculate Ro
    print(f"Calibration complete. Ro = {ro:.2f} kΩ")
    return ro

# Function to estimate NH3 concentration (PPM)
def get_ammonia_ppm(rs, ro):
    ratio = rs / ro  # Rs/Ro ratio
    ppm = 116.6020682 * (ratio ** -2.769034857)  # NH3 equation from datasheet
    return ppm

# Main function
def main():
    ro = calibrate_sensor()  # Get Ro value

    try:
        while True:
            # Read MQ-135 sensor
            adc_value = read_adc(MQ135_CHANNEL)
            rs = get_resistance(adc_value)
            ammonia_ppm = get_ammonia_ppm(rs, ro)
            print(f"MQ-135 - ADC: {adc_value}, Rs: {rs:.2f} kΩ, NH3: {ammonia_ppm:.2f} ppm")
            
            # Read pH sensor
            ph_value = ser.readline().decode('utf-8').strip()
            if ph_value:
                print(f"pH Sensor Reading: {ph_value}")
            
            # Read DHT11 sensor
            result = sensor.read()
            if result.is_valid():
                print(f"DHT11 - Temperature: {result.temperature:.1f}°C, Humidity: {result.humidity:.1f}%")
            else:
                print("DHT11 - Failed to read data.")
            
            # Check ammonia levels
            if ammonia_ppm > BASE_AMMONIA_PPM:
                print("Warning! High ammonia levels detected!")
            
            print("-----------------------------")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exiting program.")
    finally:
        ser.close()
        GPIO.cleanup()

# Run the program
if __name__ == "__main__":
    main()
