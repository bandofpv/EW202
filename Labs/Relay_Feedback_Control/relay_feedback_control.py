import ttyacm
import time
from machine import Pin, ADC, PWM

# conversion constants
# a = 0.206432038834951
# b = 5.156067961165052
a = 0.189851688407121
b = 5.459128681940197
c = 1.279819225707028e-08
e = -0.001088443757007
f = 26.564959148404913

dV = 0.3 # incremental voltage

tty = ttyacm.open(1) # open data port

sensor = ADC(Pin(26)) # create ADC object for Pin 26
motor = PWM(Pin(16)) # DC motor control from GPIO16
motor.freq(1000) # set frequency to 1KHz -- DO NOT CHANGE
motor.duty_u16(0) # 0-65535 for duty cycle range 0-100

# read 3 values and return the minimum
def sample_sensor():
    val0 = sensor.read_u16()
    time.sleep_us(1500) #IMPORTANT time.sleep(float--> rounded to nearest ms)
    val1 = sensor.read_u16()
    time.sleep_us(1500)
    val2 = sensor.read_u16()
    return min([val0,val1,val2])

# calculate height given ADC voltage
def calc_height(voltage):
    hole = c*(voltage^2) + e*voltage + f # calculate hole given ADC voltage
    return (14-hole)*2

# calculate baseline voltage given linear fit line
def calc_vb(height):
    return a * height + b

# calculate duty cycle given fan voltage
def calc_dc(voltage):
    return int(65535 * (voltage/12)) # assume 12V supply voltage

while True:
    print("Waiting on MATLAB desired height")
    desired_height = int(tty.readline()) # recieve MATLAB message for desired height
    vb = calc_vb(desired_height) # calculate base voltage
    fan_v = vb # set fan voltage to base voltage
    motor.duty_u16(calc_dc(fan_v)) # turn motor to fan voltage
    
    print("Waiting on MATLAB number of samples")
    samples = int(tty.readline()) # receive MATLAB message to collect number of samples via serial
    
    # loop for through every sample
    for i in range(samples):
        voltage = sample_sensor() # take a voltage reading
        height = calc_height(voltage) # convert voltage reading to height
        tty.print(height) # send distance to MATLAB via serial
        
        error = height - desired_height # calculate error
        
        # if ball is below desired height, increase fan voltage 
        if error < 0:
            fan_v = vb + dV # incerase by incremental voltage
            print(f"increase H: {height} V: {fan_v}")
            
        # if ball is above desired height, decrease fan voltage
        else:
            fan_v = vb - dV # decease by incremental voltage
            print(f"decrease H: {height} V: {fan_v}")
        
        fan_v = 12 if fan_v > 12 else fan_v # max fan_v to 12 volts 
            
        motor.duty_u16(calc_dc(fan_v)) # turn motor to fan_v
        
        time.sleep(0.02) # sampling period 0.02 seconds
    
    motor.duty_u16(0) # turn off motor when done
    print("Done")
