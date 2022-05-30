from collections import namedtuple
from machine import I2C

DS3231DateTime = namedtuple('DS3231DateTime', ('year', 'month', 'date', 'day', 'hour', 'minute', 'second'))
DS3231Alarm = namedtuple('DS3231Alarm', ('date', 'day', 'hour', 'minute', 'second'))
DS3231Control = namedtuple('DS3231Control', ('eosc', 'bbsqw', 'conv', 'sqw_frq', 'intcn', 'a2ie', 'a1ie'))
DS3231Status = namedtuple('DS3231Status', ('osf', 'en32khz', 'bsy', 'a2f', 'a1f'))

class DS3231:

    __DATE_TIME_REGISTER   = 0x00
    __ALARM_1_REGISTER     = 0x07
    __ALARM_2_REGISTER     = 0x0b
    __CONTROL_REGISTER     = 0x0e
    __STATUS_REGISTER      = 0x0f
    __TEMPERATURE_REGISTER = 0x11

    ALARM_1 = 0
    ALARM_2 = 1

    SQW_FRQ_1    = 0b00
    SQW_FRQ_1024 = 0b01
    SQW_FRQ_4096 = 0b10
    SQW_FRQ_8192 = 0b11

    __i2c_bus: I2C = None
    __i2c_address: int = None

    @staticmethod
    def bcd_to_binary(bcd: int) -> int:
        return bcd - 6 * (bcd >> 4)

    @staticmethod
    def binary_to_bcd(binary: int) -> int:
        return binary + 6 * (binary // 10)

    @staticmethod
    def parse_hour(hour_register_value: int) -> int:
        hour = None
        is_24_hour_format = (hour_register_value >> 6 & 0b1) == 0
        if is_24_hour_format:
            hour = DS3231.bcd_to_binary(hour_register_value & 0b00111111)

        else:
            hour = DS3231.bcd_to_binary(hour_register_value & 0b00011111)
            is_am = (hour_register_value >> 5 & 0b1) == 0
            if is_am and hour == 12:
                hour = 0

            elif not is_am and hour != 12:
                hour += 12

        return hour

    @staticmethod
    def buffer_to_date_time(buffer: bytes) -> DS3231DateTime:
        year_register_value = buffer[6]
        month_register_value = buffer[5]
        date_register_value = buffer[4]
        day_register_value = buffer[3]
        hour_register_value = buffer[2]
        minute_register_value = buffer[1]
        second_register_value = buffer[0]

        year = 2000 \
                + ((month_register_value >> 7 & 0b1) * 100) \
                + DS3231.bcd_to_binary(year_register_value)

        hour = DS3231.parse_hour(hour_register_value & 0b01111111)

        return DS3231DateTime(
            year,
            DS3231.bcd_to_binary(month_register_value  & 0b00011111),
            DS3231.bcd_to_binary(date_register_value   & 0b00111111),
            DS3231.bcd_to_binary(day_register_value    & 0b00000111),
            hour,
            DS3231.bcd_to_binary(minute_register_value & 0b01111111),
            DS3231.bcd_to_binary(second_register_value & 0b01111111)
            )

    @staticmethod
    def date_time_to_buffer(date_time: DS3231DateTime) -> bytes:
        month = DS3231.binary_to_bcd(date_time.month) & 0b00011111
        if date_time.year >= 2100:
            month = month | 0b10000000

        return bytes([
            DS3231.binary_to_bcd(date_time.second)     & 0b01111111,
            DS3231.binary_to_bcd(date_time.minute)     & 0b01111111,
            DS3231.binary_to_bcd(date_time.hour)       & 0b00111111,
            DS3231.binary_to_bcd(date_time.day)        & 0b00000111,
            DS3231.binary_to_bcd(date_time.date)       & 0b00111111,
            month,
            DS3231.binary_to_bcd(date_time.year % 100) & 0b11111111
            ])

    @staticmethod
    def buffer_to_alarm(buffer: bytes, include_second: bool) -> DS3231Alarm:
        date_register_value = buffer[2 + include_second]
        hour_register_value = buffer[1 + include_second]
        minute_register_value = buffer[0 + include_second]
        second_register_value = buffer[0]

        date = None
        day = None
        has_date = (date_register_value >> 7 & 0b1) == 0
        if has_date:
            is_date = (date_register_value >> 6 & 0b1) == 0
            if is_date:
                date = DS3231.bcd_to_binary(date_register_value & 0b00111111)

            else:
                day = DS3231.bcd_to_binary(date_register_value & 0b00000111)

        hour = None
        has_hour = (hour_register_value >> 7 & 0b1) == 0
        if has_hour:
            hour = DS3231.parse_hour(hour_register_value)

        minute = None
        has_minute = (minute_register_value >> 7 & 0b1) == 0
        if has_minute:
            minute = DS3231.bcd_to_binary(minute_register_value & 0b01111111)

        second = None
        has_second = include_second and (second_register_value >> 7 & 0b1) == 0
        if has_second:
            second = DS3231.bcd_to_binary(second_register_value & 0b01111111)

        return DS3231Alarm(
            date,
            day,
            hour,
            minute,
            second
            )

    @staticmethod
    def alarm_to_buffer(alarm: DS3231Alarm, include_second: bool) -> bytes:
        date = 0b10000000
        if alarm.date is not None:
            date = DS3231.binary_to_bcd(alarm.date) & 0b00111111

        if alarm.day is not None:
            date = DS3231.binary_to_bcd(alarm.day) & 0b00000111 | 0b01000000

        hour = 0b10000000
        if alarm.hour is not None:
            hour = DS3231.binary_to_bcd(alarm.hour) & 0b00111111

        minute = 0b10000000
        if alarm.minute is not None:
            minute = DS3231.binary_to_bcd(alarm.minute) & 0b01111111

        second = 0b10000000
        if alarm.second is not None:
            second = DS3231.binary_to_bcd(alarm.second) & 0b01111111

        if include_second:
            return bytes([
                second,
                minute,
                hour,
                date
                ])
        
        else:
            return bytes([
                minute,
                hour,
                date
                ])

    @staticmethod
    def buffer_to_control(buffer: bytes) -> DS3231Control:
        return DS3231Control(
            (buffer[0] >> 7 & 0b1) == 1, # eosc
            (buffer[0] >> 6 & 0b1) == 1, # bbsqw
            (buffer[0] >> 5 & 0b1) == 1, # conv
             buffer[0] >> 3 & 0b11, # sqw_frq
            (buffer[0] >> 2 & 0b1) == 1, # intcn
            (buffer[0] >> 1 & 0b1) == 1, # a2ie
            (buffer[0] >> 0 & 0b1) == 1 # a1ie
            )

    @staticmethod
    def control_to_buffer(control: DS3231Control) -> bytes:
        return bytes([
            control.eosc    << 7 |
            control.bbsqw   << 6 |
            control.conv    << 5 |
            control.sqw_frq << 3 |
            control.intcn   << 2 |
            control.a2ie    << 1 |
            control.a1ie    << 0
            ])

    @staticmethod
    def buffer_to_status(buffer: bytes) -> DS3231Status:
        return DS3231Status(
            (buffer[0] >> 7 & 0b1) == 1, # osf
            (buffer[0] >> 3 & 0b1) == 1, # en32khz
            (buffer[0] >> 2 & 0b1) == 1, # bsy
            (buffer[0] >> 1 & 0b1) == 1, # a2f
            (buffer[0] >> 0 & 0b1) == 1 # a1f
            )

    @staticmethod
    def status_to_buffer(status: DS3231Status) -> bytes:
        return bytes([
            status.osf     << 7 |
            status.en32khz << 3 |
            status.bsy     << 2 |
            status.a2f     << 1 |
            status.a1f     << 0
            ])

    @staticmethod
    def buffer_to_temperature(buffer: bytes) -> float:
        integer_register_value = buffer[0]
        fraction_register_value = buffer[1]

        temperature = None
        is_positive = (integer_register_value >> 7 & 0b1) == 0
        if is_positive:
            temperature = integer_register_value

        else:
            temperature = (integer_register_value - 0b1 ^ 0b11111111) * -1

        temperature = temperature \
                + ((fraction_register_value >> 7 & 0b1) * (2 ** -1)) \
                + ((fraction_register_value >> 6 & 0b1) * (2 ** -2))

        return temperature

    def __init__(self, i2c_bus: I2C, i2c_address: int = 0x68):
        self.__i2c_bus = i2c_bus
        self.__i2c_address = i2c_address

    def __get_register(self, register: int, register_size: int = 1) -> bytes:
        return self.__i2c_bus.readfrom_mem(self.__i2c_address, register, register_size)

    def __set_register(self, register: int, buffer: bytes):
        self.__i2c_bus.writeto_mem(self.__i2c_address, register, buffer)

    def get_date_time(self) -> DS3231DateTime:
        buffer = self.__get_register(self.__DATE_TIME_REGISTER, 7)
        return DS3231.buffer_to_date_time(buffer)

    def set_date_time(self, date_time: DS3231DateTime):
        buffer = DS3231.date_time_to_buffer(date_time)
        self.__set_register(self.__DATE_TIME_REGISTER, buffer)

    def get_alarm(self, alarm_id: int) -> DS3231Alarm:
        alarm_register = None
        register_size = None
        include_second = None
        if alarm_id == self.ALARM_1:
            alarm_register = self.__ALARM_1_REGISTER
            register_size = 4
            include_second = True

        else:
            alarm_register = self.__ALARM_2_REGISTER
            register_size = 3
            include_second = False

        buffer = self.__get_register(alarm_register, register_size)
        return DS3231.buffer_to_alarm(buffer, include_second)

    def set_alarm(self, alarm_id: int, alarm: DS3231Alarm):
        alarm_register = None
        include_second = None
        if alarm_id == self.ALARM_1:
            alarm_register = self.__ALARM_1_REGISTER
            include_second = True

        else:
            alarm_register = self.__ALARM_2_REGISTER
            include_second = False

        buffer = DS3231.alarm_to_buffer(alarm, include_second)
        self.__set_register(alarm_register, buffer)

    def get_control(self) -> DS3231Control:
        buffer = self.__get_register(self.__CONTROL_REGISTER)
        return DS3231.buffer_to_control(buffer)

    def set_control(self, control: DS3231Control):
        buffer = DS3231.control_to_buffer(control)
        self.__set_register(self.__CONTROL_REGISTER, buffer)

    def get_status(self) -> DS3231Status:
        buffer = self.__get_register(self.__STATUS_REGISTER)
        return DS3231.buffer_to_status(buffer)

    def set_status(self, status: DS3231Status):
        buffer = DS3231.status_to_buffer(status)
        self.__set_register(self.__STATUS_REGISTER, buffer)
    
    def get_temperature(self) -> float:
        buffer = self.__get_register(self.__TEMPERATURE_REGISTER, 2)
        return DS3231.buffer_to_temperature(buffer)
