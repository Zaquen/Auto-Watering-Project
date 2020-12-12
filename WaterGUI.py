import pandas as pd # For Data Manipulation
import seaborn as sns # For graphing
import matplotlib.pyplot as plt # Also for graphing
import PySimpleGUI as sg # For the GUI
import time # For the time and date
import RPi.GPIO as GPIO # For the watering buttons

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

#Function to turn the water pump on and then off
def waterPlant(pump):
    GPIO.output(pump, GPIO.HIGH) # Turn the pump on for 4 seconds
    time.sleep(4)
    GPIO.output(pump, GPIO.LOW) # Turn the pump off

# Grab data from github, format it in pandas
data = pd.read_csv('https://raw.githubusercontent.com/Zaquen/SeniorProject/master/data.txt?token=ANH2CXFO4SBA6IWVOH4IHR273Y7K6')
data.columns = ['Timestamp', 'Soil_A', 'Soil_B', 'WaterLevel', 'Day_A', 'Day_B', 'Temp', 'Humid']

# Data manipulation, make it readable
# Make a new column for a date and time
# Make the soil moisture a percentage up to 500 as 100%
# Make the day sensors a percentage up to 1024 as 100%
# Drop the waterLevel column
data = data.drop(columns='WaterLevel')
data.Soil_A = (data.Soil_A / 500) * 100
data.Soil_B = (data.Soil_B / 500) * 100
data.Day_A = ((data.Day_A / 1024) * 100).round(2)
data.Day_B = ((data.Day_B / 1024) * 100).round(2)
data['Datetime'] = pd.to_datetime(data.Timestamp, unit='s')
data['Time'] = pd.to_datetime(data.Datetime).dt.time

#All of my graphs I want to show, save them to files for the GUI, then clear the plot
plot = sns.lineplot(data=data, y=data.Temp, x=data.Datetime) # Temp/Time
plot.set(xlabel='Time since 12/10')
plot.set(xticklabels=[])
plt.savefig('temp.png', bbox_inches='tight')
plt.clf()

plot = sns.lineplot(data=data, y=data.Humid, x=data.Datetime) # Humid/Time
plot.set(xlabel='Time since 12/10')
plot.set(xticklabels=[])
plt.savefig('humid.png', bbox_inches='tight')
plt.clf()

plot = sns.lineplot(data=data, y=data.Soil_A, x=data.Datetime) # SoilA/Time
plot.set(xlabel='Time since 12/10')
plot.set(xticklabels=[])
plt.savefig('soila.png', bbox_inches='tight')
plt.clf()

plot = sns.lineplot(data=data, y=data.Soil_B, x=data.Datetime) # SoilB/Time
plot.set(xlabel='Time since 12/10')
plot.set(xticklabels=[])
plt.savefig('soilb.png', bbox_inches='tight')
plt.clf()

plot = sns.lineplot(data=data, y=data.Day_A, x=data.Datetime) # DaylightA/Time
plot.set(xlabel='Time since 12/10')
plot.set(xticklabels=[])
plt.savefig('daya.png', bbox_inches='tight')
plt.clf()

plot = sns.lineplot(data=data, y=data.Day_B, x=data.Datetime) # DaylightB/Time
plot.set(xlabel='Time since 12/10')
plot.set(xticklabels=[])
plt.savefig('dayb.png', bbox_inches='tight')
plt.clf()

#Build the window

#Layout first
#Setup the 3 columns
column_left = [
    [sg.Text("Plant A Moisture over Time")],[sg.Image('soila.png')],
    [sg.Text("Plant A Daylight over Time")],[sg.Image('daya.png')],
    [sg.Button('Water Plant A')],
    ]
column_center = [
    [sg.Text("Temperature over Time")],[sg.Image('temp.png')],
    [sg.Text('Humidity over Time')],[sg.Image('humid.png')],
    ]
column_right = [
    [sg.Text("Plant B Moisture over Time")],[sg.Image('soilb.png')],
    [sg.Text("Plant B Daylight over Time")],[sg.Image('dayb.png')],
    [sg.Button('Water Plant B')],
    ]

layout = [
    [
        sg.Column(column_left),
        sg.VSeperator(),
        sg.Column(column_center),
        sg.VSeperator(),
        sg.Column(column_right),
    ]
]

# Create the Window
window = sg.Window(title='Plant Watering', layout=layout, location=(0,0),
                   element_justification='center', font="Helvetica 16", finalize=True)

# Create an event loop
while True:
    event, values = window.read()
    
    # Handle the case of Water Plant Buttons
    if event == 'Water Plant A':
        waterPlant(PUMP1)
    if event == 'Water Plant B':
        waterPlant(PUMP2)
        # End program if user closes window
    if event == sg.WIN_CLOSED:
        break

window.close()