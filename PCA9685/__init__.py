from periphery import I2C
import time
import math
import logging

# 寄存器地址等
PCA9685_ADDRESS    = 0x40  # PCA9685 I2C 地址
MODE1              = 0x00  # 模式寄存器1
MODE2              = 0x01  # 模式寄存器2
PRESCALE           = 0xFE  # 预分频寄存器
LED0_ON_L          = 0x06  # 第0路LED开启时间低字节
LED0_ON_H          = 0x07  # 第0路LED开启时间高字节
LED0_OFF_L         = 0x08  # 第0路LED关闭时间低字节
LED0_OFF_H         = 0x09  # 第0路LED关闭时间高字节
ALL_LED_ON_L       = 0xFA  # 所有LED开启时间低字节
ALL_LED_ON_H       = 0xFB  # 所有LED开启时间高字节
ALL_LED_OFF_L      = 0xFC  # 所有LED关闭时间低字节
ALL_LED_OFF_H      = 0xFD  # 所有LED关闭时间高字节

# 位操作
RESTART            = 0x80  # 重启
SLEEP              = 0x10  # 休眠
ALLCALL            = 0x01  # 响应所有呼叫
INVRT              = 0x10  # 输出逻辑反转
OUTDRV             = 0x04  # 输出驱动

logger = logging.getLogger(__name__)

class PCA9685:
    """使用 periphery 控制 PCA9685 PWM LED/伺服控制器。"""

    def __init__(self, address=PCA9685_ADDRESS, i2c_dev="/dev/i2c-1"):
        """初始化 PCA9685。"""
        self.i2c = I2C(i2c_dev)  # 初始化 I2C 设备
        self.address = address  # 设置 I2C 地址
        self.set_all_pwm(0, 0)  # 关闭所有 PWM 通道
        self.write_byte(MODE2, OUTDRV)  # 设置模式2寄存器
        self.write_byte(MODE1, ALLCALL)  # 设置模式1寄存器
        time.sleep(0.005)  # 等待振荡器稳定
        mode1 = self.read_byte(MODE1)
        mode1 = mode1 & ~SLEEP  # 取消休眠模式
        self.write_byte(MODE1, mode1)
        time.sleep(0.005)  # 等待振荡器稳定

    def write_byte(self, reg, value):
        """向寄存器写入一个字节。"""
        self.i2c.transfer(self.address, [I2C.Message([reg, value])])

    def read_byte(self, reg):
        """从寄存器读取一个字节。"""
        read = I2C.Message([0], read=True)
        self.i2c.transfer(self.address, [I2C.Message([reg]), read])
        return read.data[0]

    def set_pwm_freq(self, freq_hz):
        """设置 PWM 频率（单位：赫兹）。"""
        prescaleval = 25000000.0    # 25MHz 振荡器频率
        prescaleval /= 4096.0       # 12 位分辨率
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        logger.debug('设置 PWM 频率为 {0} Hz'.format(freq_hz))
        logger.debug('估算预分频值: {0}'.format(prescaleval))
        prescale = int(math.floor(prescaleval + 0.5))
        logger.debug('最终预分频值: {0}'.format(prescale))
        oldmode = self.read_byte(MODE1)
        newmode = (oldmode & 0x7F) | 0x10    # 进入休眠模式
        self.write_byte(MODE1, newmode)  # 设置寄存器进入休眠模式
        self.write_byte(PRESCALE, prescale)  # 设置预分频寄存器
        self.write_byte(MODE1, oldmode)
        time.sleep(0.005)
        self.write_byte(MODE1, oldmode | 0x80)

    def set_pwm(self, channel, on, off):
        """设置单个 PWM 通道。"""
        self.write_byte(LED0_ON_L+4*channel, on & 0xFF)
        self.write_byte(LED0_ON_H+4*channel, on >> 8)
        self.write_byte(LED0_OFF_L+4*channel, off & 0xFF)
        self.write_byte(LED0_OFF_H+4*channel, off >> 8)

    def set_all_pwm(self, on, off):
        """设置所有 PWM 通道。"""
        self.write_byte(ALL_LED_ON_L, on & 0xFF)
        self.write_byte(ALL_LED_ON_H, on >> 8)
        self.write_byte(ALL_LED_OFF_L, off & 0xFF)
        self.write_byte(ALL_LED_OFF_H, off >> 8)
