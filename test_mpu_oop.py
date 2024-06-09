from machine import SoftI2C, Pin, UART, Timer
import time
import math
from collections import deque

from moto import Moto
import mpu6050

class IMUController:
    def __init__(self):
        # 初始化硬件接口
        self.i2c1 = SoftI2C(scl=Pin(42), sda=Pin(41))
        self.mpu = mpu6050.accel(self.i2c1)
        self.uart = UART(1, 115200, rx=12, tx=11)
        self.uart.write('Hello 01Studio!\n')
        
        # 初始化参数
        self.alpha = 0.5
        self.dt = 0.01
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.yaw_deg = 0
        self.yaw_last = 0
        self.yaw_offset = 0
        
        self.yaw_offset_values = []
        self.pitch_deg_values = []
        self.roll_deg_values = []
        self.yaw_fix_values = []
        
        self.moto = Moto(1,2)
    
    def window_filter(self, value, values, window_size=50):
        values.append(value)
        # 如果列表长度超过窗口大小，则移除最旧的元素
        if len(values) > window_size:
            values.pop(0)

        return sum(values) / len(values)

    def read_data_and_update(self,tim_1):
        data = self.mpu.get_values()
        acc  = data['AcX'], data['AcY'], data['AcZ']
        gyro = data['GyX'], data['GyY'], data['GyZ']

        roll_acc  = math.atan2(acc[1], acc[2])
        pitch_acc = math.atan2(-acc[0], math.sqrt(acc[1]**2 + acc[2]**2))

        self.pitch = (1 - self.alpha) * (self.pitch + gyro[0] * self.dt * 0.001) + self.alpha * pitch_acc
        self.roll  = (1 - self.alpha) * (self.roll  + gyro[1] * self.dt * 0.001) + self.alpha * roll_acc

        self.pitch_deg = self.pitch * 180/math.pi
        self.roll_deg  = self.roll  * 180/math.pi

        self.yaw    += gyro[2]  * self.dt * 0.001 - 0.000929
        self.yaw_deg = self.yaw * 180/math.pi

        self.yaw_offset = self.yaw - self.yaw_last
        self.yaw_last   = self.yaw

        self.yaw_offset_avg = self.window_filter(self.yaw_offset, self.yaw_offset_values, 100)

        self.pitch_deg = self.window_filter(self.pitch_deg, self.pitch_deg_values, 5)
        self.roll_deg  = self.window_filter(self.roll_deg,  self.roll_deg_values,  5)
        self.yaw_deg   = self.window_filter(self.yaw_deg,   self.yaw_fix_values,   5)

        self.print_and_send_data()

    def control_motor(self,tim_2):
        abs_roll_deg = abs(self.roll_deg)
        if abs_roll_deg > 10:
            speed = int(self.roll_deg / 90 * 1023)
            self.moto.setSpeed(speed)
        else:
            self.moto.setSpeed(0)

    def print_and_send_data(self):
        prt_msg = f"roll = {self.roll_deg:.2f}  pitch = {self.pitch_deg:.2f}  yaw = {self.yaw_deg:.2f}  yaw_offset = {self.yaw_offset:.2f}  avg_yaw_offset = {self.yaw_offset_avg:.2f}"
        print(prt_msg)
        uart_msg = f"test:{self.roll_deg:.2f},{self.pitch_deg:.2f},{self.yaw_deg:.2f}\n"
        self.uart.write(uart_msg)

    def setup_timers(self):
        tim_1 = Timer(1)
        tim_1.init(period=int(self.dt*1000), mode=Timer.PERIODIC, callback=self.read_data_and_update)

        tim_2 = Timer(2)
        tim_2.init(period=int(self.dt*1000), mode=Timer.PERIODIC, callback=self.control_motor)

if __name__ == "__main__":
    imu_controller = IMUController()
    imu_controller.setup_timers()

    # while True:
    #     pass  # 主循环保持程序运行

"""
在这个版本中，我们定义了一个 IMUController 类，它包含了初始化硬件、读取数据、更新姿态角、控制电机、打印数据及发送串口数据的方法。同时，我们还定义了两个定时器回调方法 read_data_and_update 和 control_motor 来分别处理数据更新和电机控制逻辑。最后，在主程序中实例化这个类并设置定时器，使得整个程序以面向对象的方式组织起来，更加清晰和易于管理。
"""