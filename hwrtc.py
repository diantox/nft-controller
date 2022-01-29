from machine import RTC
from urtc import seconds2tuple, DS3231
import config
import ntptime
import time

hwrtc = None
ds3231 = None


def initialize_hwrtc():
    global hwrtc

    if hwrtc is not None:
        print('HW RTC is already initialized')

    else:
        print('Initializing HW RTC...')

        hwrtc = RTC()

        print('HW RTC initialized')
        print('HW RTC time:', hwrtc.datetime())


def initialize_ds3231():
    global ds3231

    if ds3231 is not None:
        print('DS3231 is already initialized')

    else:
        print('Initializing DS3231...')

        ds3231 = DS3231(config.i2c)

        print('DS3231 initialized')
        print('DS3231 time:', ds3231.datetime())


def synchronize_hwrtc_ds3231():
    global hwrtc
    global ds3231

    try:
        print('Synchronizing HW RTC and DS3231 from an NTP server...')

        unix_time = ntptime.time()
        named_time_tuple = seconds2tuple(unix_time)
        time_tuple = tuple(named_time_tuple)

        hwrtc.datetime(time_tuple)
        ds3231.datetime(time_tuple)

        print('Synchronized HWC RTC and DS3231 from an NTP server')
        print('HW RTC time:', hwrtc.datetime())
        print('DS3231 time:', ds3231.datetime())

    except BaseException:
        print('Failed to synchronize HW RTC and DS3231 from an NTP server')
        print('Synchronizing HW RTC from DS3231...')

        named_time_tuple = ds3231.datetime()
        time_tuple = tuple(named_time_tuple)[:7] + (0,)
        hwrtc.datetime(time_tuple)

        print('Synchronized HW RTC from DS3231')
        print('HW RTC time:', hwrtc.datetime())
        print('DS3231 time:', ds3231.datetime())
