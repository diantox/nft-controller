from machine import Pin
import config
import time

pump_enable = False
led_enable = False


def toggle_pump_enable():
    global pump_enable

    pump_enable = not pump_enable
    config.pump_enable.value(pump_enable)


def toggle_led_enable():
    global led_enable

    led_enable = not led_enable
    config.led_channel_0_enable.value(led_enable)
    config.led_channel_1_enable.value(led_enable)


def debounce_pin(pin, milliseconds):
    current_pin_value = pin.value()
    current_milliseconds = 0

    while current_milliseconds < milliseconds:
        if pin.value() != current_pin_value:
            current_milliseconds += 1

        else:
            current_milliseconds = 0

        time.sleep_ms(1)


def pump_interrupt_handler(pin):
    debounce_pin(pin, 17)
    toggle_pump_enable()


def led_interrupt_handler(pin):
    debounce_pin(pin, 17)
    toggle_led_enable()


def register_pump_led_interrupt_handlers():
    config.pump_interrupt.irq(
        handler=pump_interrupt_handler,
        trigger=Pin.IRQ_FALLING
    )

    config.led_interrupt.irq(
        handler=led_interrupt_handler,
        trigger=Pin.IRQ_FALLING
    )
