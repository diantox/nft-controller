import hwrtc
import wlan


def main():
    # wlan.initialize_wlan()
    # wlan.connect_to_wlan()

    hwrtc.initialize_hwrtc()
    hwrtc.initialize_ds3231()
    hwrtc.synchronize_hwrtc_ds3231()


main()
