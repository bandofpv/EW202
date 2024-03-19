import time
from machine import Pin, ADC

sensor = ADC(Pin(26)) # create ADC object for Pin 26

# conversion constants
c = 1.279819225707028e-08
e = -0.001088443757007
f = 26.564959148404913

# convert ADC voltage to hole number
def calc_hole(voltage):
    return c*(voltage^2) + e*voltage + f

# convert hole number to height in cm
def calc_height(hole):
    return (14-hole)*2

while True:
    voltage = sensor.read_u16() # get sensor ADC reading
    hole = calc_hole(voltage) # calculate hole number
    height = calc_height(hole) # calculate height in cm
    print(f"Height: {height}cm") # print height
    time.sleep(0.25)