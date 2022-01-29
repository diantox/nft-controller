from machine import I2C, Pin
from tinypico import I2C_SCL, I2C_SDA

i2c = I2C(scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))

ds3231_interrupt = Pin(33)
ads1115_interrupt = Pin(32)

pump_enable = Pin(24)
led_channel_0_enable = Pin(17)
led_channel_1_enable = Pin(21)

pump_interrupt = Pin(16)
led_interrupt = Pin(15)

wlan_reconnects = 3
wlan_ssid = ''
wlan_password = ''
