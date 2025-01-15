import serial
# Configure the serial connection
ser = serial.Serial(
 port='/dev/ttyS0', # Replace with your serial port
 baudrate=9600, # Adjust baudrate as per your sensor's specifications
 timeout=1 # Set a timeout for reading
)
print("Reading data from pH sensor...")
try:
 while True:
    if ser.in_waiting > 0: # Check if there's data waiting in the serial buffer
        line = ser.readline().decode('utf-8').strip() # Read and decode a line
        print(line) # Print the line to the terminal
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        ser.close() # Close the serial connection when done