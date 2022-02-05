from machine import I2C, Pin
from tinypico import I2C_SCL, I2C_SDA

i2c = I2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))

ds3231_interrupt = Pin(15, Pin.IN, Pin.PULL_UP)
ads1115_interrupt = Pin(27, Pin.IN, Pin.PULL_UP)

pump_enable = Pin(14, Pin.OUT, Pin.PULL_DOWN, value=0)
led_channel_0_enable = Pin(33, Pin.OUT, Pin.PULL_DOWN, value=0)
led_channel_1_enable = Pin(32, Pin.OUT, Pin.PULL_DOWN, value=0)

pump_interrupt = Pin(26, Pin.IN, Pin.PULL_UP)
led_interrupt = Pin(25, Pin.IN, Pin.PULL_UP)

wlan_reconnects = 3
wlan_ssid = ''
wlan_password = ''
