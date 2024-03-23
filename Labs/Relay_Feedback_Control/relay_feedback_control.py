import ttyacm
import time
from machine import Pin, ADC

# conversion constants
c = 1.279819225707028e-08
e = -0.001088443757007
f = 26.564959148404913

tty = ttyacm.open(1) # open data port

sensor = ADC(Pin(26)) # create ADC object for Pin 26

# read 3 values and return the minimum
def sample_sensor():
    val0 = sensor.read_u16()
    time.sleep_us(1500) #IMPORTANT time.sleep(float--> rounded to nearest ms)
    val1 = sensor.read_u16()
    time.sleep_us(1500)
    val2 = sensor.read_u16()
    return min([val0,val1,val2])

# convert ADC voltage to distance in cm
def convert(voltage):
    hole = c*(voltage^2) + e*voltage + f # calculate hole given ADC voltage
    return (14-hole)*2 

while True:
    print("Waiting on MATLAB")
    samples = tty.readline() # receive MATLAB message to collect number of samples via serial

    for i in range(samples):
        voltage = sample_sensor() # take a voltage reading
        distance = convert(voltage) # convert voltage reading to distance
        tty.print(distance) # send distance to MATLAB via serial
        print(distance)
        time.sleep(0.02) # sampling period 0.02 seconds
