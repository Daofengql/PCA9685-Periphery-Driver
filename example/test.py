from PCA9685 import PCA9685
import time
import math

# 创建 PCA9685 实例
pwm = PCA9685(i2c_dev="/dev/i2c-5")
pwm.set_pwm_freq(60)  # 通常舵机使用50-60Hz的PWM信号

def set_servo_angle(pwm_driver, channel, angle):
    """
    设置舵机的角度。

    :param pwm_driver: PCA9685 PWM 驱动实例
    :param channel: 需要设置的 PWM 通道
    :param angle: 目标角度（0-180度）
    """
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    pulse_length //= 4096     # 12 bits of resolution
    pulse = int((angle * 11.11) + 500) # 转换角度到脉宽 (500-2500us)
    pulse //= pulse_length
    pwm_driver.set_pwm(channel, 0, pulse)

def breathe_servo(pwm_driver, channel, min_angle=0, max_angle=180, step=1, base_delay=0.01):
    """
    实现舵机的呼吸效果。

    :param pwm_driver: PCA9685 PWM 驱动实例
    :param channel: 需要设置的 PWM 通道
    :param min_angle: 最小角度 (默认0度)
    :param max_angle: 最大角度 (默认180度)
    :param step: 每次变化的角度步长 (默认1度)
    :param base_delay: 基础延迟时间 (默认0.05秒)
    """
    while True:
        # 逐渐增加角度并加快速度
        for angle in range(min_angle, max_angle, step):
            set_servo_angle(pwm_driver, channel, angle)
            time.sleep(base_delay * (1 - (angle / max_angle)))
        
        # 逐渐减少角度并减慢速度
        for angle in range(max_angle, min_angle, -step):
            set_servo_angle(pwm_driver, channel, angle)
            time.sleep(base_delay * (angle / max_angle))

# 启动舵机呼吸效果
breathe_servo(pwm, channel=0)
