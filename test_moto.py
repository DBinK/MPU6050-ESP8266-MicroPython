from machine import Timer
from moto import Moto

moto = Moto(1,2)

for i in range(0, 1023, 10):
    moto.setSpeed(i)
    time.sleep_ms(20)

for i in range(0, -1023, -10):
    moto.setSpeed(i)
    time.sleep_ms(20)

print("test end")
        
def control(tim_2):
    moto.setSpeed(0)

tim_2 = Timer(2)
tim_2.init(period=int(100), mode=Timer.PERIODIC,callback=control) 
