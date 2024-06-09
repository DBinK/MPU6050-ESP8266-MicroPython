from machine import SoftI2C, Pin, UART, Timer
import time
import math

from moto import Moto
import mpu6050

# 构建I2C对象
i2c1 = SoftI2C(scl=Pin(42), sda=Pin(41))

# 构建MPU6050对象
mpu = mpu6050.accel(i2c1)

uart = UART(1, 115200, rx=12, tx=11)  # 设置串口号1和波特率
uart.write('Hello 01Studio!')  # 发送一条数据

# 初始化互补滤波参数
alpha = 0.5 # 陀螺仪计权重

dt = 0.01  # 采样间隔

roll = 0
pitch = 0
yaw = 0
yaw_deg = 0
yaw_last = 0
yaw_offset = 0  # 零漂补偿值

# 创建deque队列用于存储yaw_offset的值
yaw_offset_values = []

# 创建用于存储pitch_deg、roll_deg和yaw_fix的值的列表
pitch_deg_values = []
roll_deg_values = []
yaw_fix_values = []

moto = Moto(1,2)

def window_filter(value, values, window_size=50):
    # 将值添加到列表中
    values.append(value)

    # 如果列表长度超过窗口大小，则移除最旧的元素
    if len(values) > window_size:
        values.pop(0)

    # 返回平均值
    return sum(values) / len(values)

def main(tim_1):
    
    global i2c1, mpu
    global alpha, dt, roll, pitch, yaw, yaw_last, yaw_offset
    global pitch_deg_values, roll_deg_values, yaw_fix_values, yaw_offset_values
    global roll_deg, pitch_deg, yaw_deg
    
    # 获取加速度计数据
    data = mpu.get_values()
    acc = data['AcX'], data['AcY'], data['AcZ']

    # 获取陀螺仪数据
    gyro = data['GyX'], data['GyY'], data['GyZ']

    # 计算加速度计的pitch、roll角度
    # 计算roll和pitch角度
    roll_acc   = math.atan2(acc[1], acc[2])
    pitch_acc  = math.atan2(-acc[0], math.sqrt(acc[1] ** 2 + acc[2] ** 2))
    
    # 使用互补滤波算法进行校正
    pitch = (1 - alpha) * (pitch + gyro[0] * dt*0.001) + alpha * pitch_acc
    roll  = (1 - alpha) * (roll  + gyro[1] * dt*0.001) + alpha * roll_acc
    
    # 将弧度转换为角度
    pitch_deg = pitch * 180/math.pi
    roll_deg  = roll  * 180/math.pi

    yaw      = yaw + gyro[2] * dt*0.001 - (0.000929) # 零漂参数
    yaw_deg  = yaw * 180/math.pi
    
    # 获取温度
    temperature = data['Tmp']

    yaw_offset = yaw - yaw_last
    yaw_last   = yaw
    
    avg_yaw_offset = window_filter(yaw_offset, yaw_offset_values, 1000)

    # 使用窗口滤波函数平滑pitch_deg、roll_deg和yaw_fix
    pitch_deg = window_filter(pitch_deg, pitch_deg_values, 10)
    roll_deg  = window_filter(roll_deg, roll_deg_values, 10)
    yaw_deg   = window_filter(yaw_deg, yaw_fix_values, 10)
    
    if pitch_deg == 0 and roll_deg == 0:
        mpu = mpu6050.accel(i2c1)
    
    # 打印数据
    x = "roll = %.2f  pitch = %.2f  yaw = %.2f  yaw_offset = %.2f  avg_yaw_offset = %.2f" % (roll_deg, pitch_deg, yaw_deg, yaw_offset, avg_yaw_offset)
    print(x)
    w = "test:%.2f,%.2f,%.2f \n" % (roll_deg, pitch_deg, yaw_deg)
    uart.write(w)  # 发送数据到串口

def control(tim_2):
    global roll_deg, pitch_deg 
    abs_roll_deg = abs(roll_deg)
    
    if abs_roll_deg > 10:
        speed = int(roll_deg/90*1023)
        moto.setSpeed(speed)
        
    elif abs_roll_deg < 10:
        moto.setSpeed(0)
    
    if pitch_deg == 0 and roll_deg == 0:
        moto.setSpeed(0)
    
#使用定时器1
tim_1 = Timer(1)
tim_1.init(period=int(dt*1000), mode=Timer.PERIODIC,callback=main) 

#使用定时器2
tim_2 = Timer(2)
tim_2.init(period=int(dt*1000), mode=Timer.PERIODIC,callback=control) 

