from machine import Pin, PWM
import time

class Moto:
    def __init__(self,speed_pin,switch_pin,signal_pin=None):
        
        self.moto_speed  = PWM(Pin(speed_pin),  freq=50, duty=0)
        self.moto_switch = PWM(Pin(switch_pin),  freq=50, duty=0)

        if signal_pin != None:
            self.moto_signal = Pin(signal_pin, Pin.IN)
        else:
            self.moto_signal = None


    def setSpeed(self,speed):
        # 限制speed在-1023~1023之间
        speed = max(-1023, min(speed, 1023))
        print(f"speed = {speed}")

        if  speed > 0:

            pwm = int(1023-speed)
            self.moto_switch.duty(1023)
            self.moto_speed.duty(pwm)

        elif speed < 0:
            
            pwm = int(1023+speed)
            self.moto_switch.duty(0)
            self.moto_speed.duty(pwm)
            
        elif speed == 0:
            period = 50
            freq = 1000//period
            self.moto_switch.duty(512)
            self.moto_switch.freq(freq)
            self.moto_speed.duty(1023)       

