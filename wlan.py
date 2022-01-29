import config
import network

network_STAT_CONNECT_FAIL = 205

wlan_status_code = {}
wlan_status_code[network.STAT_IDLE] = 'Idle'
wlan_status_code[network.STAT_CONNECTING] = 'Connecting'
wlan_status_code[network.STAT_WRONG_PASSWORD] = 'Wrong Password'
wlan_status_code[network.STAT_NO_AP_FOUND] = 'No AP Found'
wlan_status_code[network_STAT_CONNECT_FAIL] = 'Connection Failed'
wlan_status_code[network.STAT_GOT_IP] = 'Connected'

wlan = None


def initialize_wlan():
    global wlan

    if wlan is not None:
        print('WLAN is already initialized')

    else:
        print('Initializing WLAN...')

        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.config(reconnects=config.wlan_reconnects)

        print('WLAN initialized')


def connect_to_wlan():
    global wlan

    if wlan.status() == network.STAT_GOT_IP:
        print('WLAN is already connected')
        print('WLAN IP:', wlan.ifconfig()[0])

    if wlan.status() == network.STAT_CONNECTING:
        print('WLAN is already connecting...')

    if wlan.status() == network.STAT_IDLE \
            or wlan.status() == network.STAT_WRONG_PASSWORD \
            or wlan.status() == network.STAT_NO_AP_FOUND \
            or wlan.status() == network_STAT_CONNECT_FAIL:
        print('Connecting to WLAN...')

        wlan.connect(config.wlan_ssid, config.wlan_password)
        while wlan.status() == network.STAT_CONNECTING:
            pass

        print('WLAN Status:', wlan_status_code[wlan.status()])
        if wlan.status() == network.STAT_GOT_IP:
            print('WLAN IP:', wlan.ifconfig()[0])
