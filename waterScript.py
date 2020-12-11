# Import Libaries for GPIO and ADC to work
import RPi.GPIO as GPIO
import spidev
import time
import Adafruit_DHT   # For the Temp/Humidity
import smtplib, ssl   # For emails!

# Setup the GPIO pins to turn the pumps on and off
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PUMP1 = 24
PUMP2 = 25

GPIO.setup(PUMP1, GPIO.OUT)
GPIO.setup(PUMP2, GPIO.OUT)

#Set the outputs to low
GPIO.output(PUMP1, GPIO.LOW)
GPIO.output(PUMP2, GPIO.LOW)

#Set up the ADC
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

#Set up the email server
port = 465 # For SSL
smtp_server = "smtp.gmail.com"
sender_email = 'zaqrasppi@gmail.com'

# Maintain privacy, and read in the receiver email from a txt file
f = open('/home/pi/receive.txt', 'r')
receiver_email = f.read()
f.close()

# Maintain privacy, read in the password from a txt file
f = open('/home/pi/password.txt', 'r')
password = f.read()
f.close()

#Message for when the plant was watered
messageWatered = """\
Subject: Plants Watered

You may need to come drain them."""

# Message for when the tank is low
messageWaterLow = """/
Subject: Water Reservoir

Your water reservoir is low."""


#Define a readadc function, adcnum is the channel we are pulling from
def readadc(adcnum):
    # Read the data in, 8 channels
    if adcnum > 7 or adcnum < 0:
        return -1 # The failure case
    r= spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

# Function to read the temp/humidity sensor
def readDHT():
    temperature_c, humidity = Adafruit_DHT.read_retry(11, 22)
    # Sensor is cheap, reads 14 degrees C higher than actual
    temperature_f = (temperature_c - 14) * (9 / 5) + 32
    #Read into a file, temp and then humidity
    f = open('/home/pi/data.txt', 'a')
    f.write('{}, {}\n'.format(temperature_f, humidity))
    f.close()
    
# A function to control the watering of plants. Go figure
def waterPlant(channel):
    pump = PUMP1 # base case
    if channel == 1: # The other one
        pump = PUMP2
    while readadc(channel) < 400:
        GPIO.output(pump, GPIO.HIGH) # Turn the pump on for 4 seconds
        time.sleep(4)
        GPIO.output(pump, GPIO.LOW) # Let the water settle for 20, check again
        time.sleep(20)
    #Let the user know that the plant was watered, may need drained
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, messageWatered)
        
# Loop for the microcontroller bit of the project
while True:
    channels = [0, 1, 2, 3, 4]   # 0, 1 Soil Moisture
                                    # 2 Water Level
                                    # 3, 4 Daylight
    # Write the timestamp to the file
    f = open('/home/pi/data.txt', 'a')
    f.write('{}, '.format(time.time()))
    f.close()
    time.sleep(1)
    # Read all of the data in, check reservoir
    for ldr_channel in channels:
        ldr_value = readadc(ldr_channel)
        if ldr_channel < 2 and ldr_value < 10: # Needs Watered
            waterPlant(ldr_channel)
        if ldr_channel == 2 and ldr_value < 800: # Check reservoir and alert user if empty
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, messageWaterLow)
        else:
            f = open('/home/pi/data.txt', 'a') # Write data to file
            f.write('{}, '.format(ldr_value))
            f.close()
    time.sleep(1)
    readDHT() # Read from the temp/humidity sensor
    time.sleep(600) # Wait 10 minutes before reading again