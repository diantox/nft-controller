from microWebSrv import MicroWebSrv
import controller


@MicroWebSrv.route('/')
def index(httpClient, httpResponse):
    response = """\
    <!DOCTYPE html>
    <html lang='en'>
        <head>
            <meta charset='utf-8' />
            <meta name='viewport' content='width=device-width,minimum-scale=1,maximum-scale=1,user-scalable=no'>
            <title>CyberController</title>
            <script>
                async function buttonHandler(event) {
                    const button = event.target
                    const url = button.dataset.url
                    const response = await fetch(url)
                    const json = await response.json()
                    const onOff = json.enable ? 'On' : 'Off'
                    button.innerText = button.innerText.replace(/(On|Off)$/, onOff)
                }
            </script>
        </head>
        <body>
            <h1>CyberController</h1>
            <button data-url='/toggle_pump_enable' onclick='buttonHandler(event)'>Pump is %s</button>
            <button data-url='/toggle_led_enable' onclick='buttonHandler(event)'>LEDs are %s</button>
        </body>
    </html>
    """ % (
        'On' if controller.pump_enable else 'Off',
        'On' if controller.led_enable else 'Off'
    )

    httpResponse.WriteResponseOk(
        contentType='text/html',
        contentCharset='utf-8',
        content=response
    )


@MicroWebSrv.route('/toggle_pump_enable')
def toggle_pump_enable_handler(httpClient, httpResponse):
    controller.toggle_pump_enable()
    response = {"enable": controller.pump_enable}
    httpResponse.WriteResponseJSONOk(obj=response)


@MicroWebSrv.route('/toggle_led_enable')
def toggle_led_enable_handler(httpClient, httpResponse):
    controller.toggle_led_enable()
    response = {"enable": controller.led_enable}
    httpResponse.WriteResponseJSONOk(obj=response)


def start_web_server():
    web_server = MicroWebSrv()
    web_server.Start(threaded=True)
