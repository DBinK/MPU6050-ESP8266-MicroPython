from machine import SoftI2C, Pin, UART, Timer
import mpu6050
import time
import math
from filter import window_filter

# 构建I2C对象
i2c1 = SoftI2C(scl=Pin(42), sda=Pin(41))

# 构建MPU6050对象
mpu = mpu6050.accel(i2c1)

uart = UART(1, 115200, rx=12, tx=11)  # 设置串口号1和波特率
uart.write('Hello MPU6050!')  # 发送一条数据

dt = 0.02  # 采样间隔 (单位:秒)

yaw = 0
yaw_deg = 0
yaw_last = 0
yaw_offset = 0  # 待测试零漂补偿值

yaw_offset_values = []
yaw_deg_values    = []

# 测试多长时间 (单位:秒)
test_time = 5

window_size = test_time/dt
print(window_size)
time.sleep(2)

#window_size = 999

cnt = 0

def main(tim):
    
    global dt, yaw, yaw_last, yaw_offset, yaw_deg
    global yaw_deg_values, yaw_offset_values
    global window_size, cnt

    # 获取陀螺仪数据
    data = mpu.get_values()
    gyro = data['GyX'], data['GyY'], data['GyZ']

    yaw      = yaw + gyro[2] * dt - (0)    # 零漂参数
    yaw_deg  = yaw * 180/math.pi * 0.001   # 不知道为什么乘个0.001数据就对了
    
    yaw_offset = yaw - yaw_last
    yaw_last   = yaw
    
    avg_yaw_offset = window_filter(yaw_offset, yaw_offset_values, window_size)

    # 使用窗口滤波函数平滑pitch_deg、roll_deg和yaw_fix
    yaw_deg   = window_filter(yaw_deg, yaw_deg_values, 10)
    
    cnt += 1
    
    # 打印数据
    x = "yaw = %f  yaw_offset = %f  avg_yaw_offset = %f  dt = %.3fs  cnt = %d" % (yaw_deg, yaw_offset, avg_yaw_offset, dt, cnt)
    print(x)
    
    w = "test:%.2f,%.2f,%.2f \n" % (0, 0, yaw_deg)
    uart.write(w)  # 发送数据到串口
    
    if cnt == window_size:
        print(f"测试完成, avg_yaw_offset = {avg_yaw_offset}")
        tim.deinit()  # 停止定时器
        
    
#使用定时器1
tim = Timer(1)
tim.init(period=int(dt*1000), mode=Timer.PERIODIC,callback=main) #周期为1000ms

