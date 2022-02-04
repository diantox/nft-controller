import config
import controller
import hwrtc
import wlan


def main():
    if config.wlan_ssid and config.wlan_password:
        wlan.initialize_wlan()
        wlan.connect_to_wlan()

    hwrtc.initialize_hwrtc()
    hwrtc.initialize_ds3231()
    hwrtc.synchronize_hwrtc_ds3231()

    controller.register_pump_led_interrupt_handlers()


main()
