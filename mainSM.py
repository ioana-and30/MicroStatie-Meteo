import network
import socket
import time
from machine import I2C, Pin, PWM
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import dht
import h2RGB
import secrets

# LCD setup
I2C_ADDR = 0x27
LCD_COLS = 20
LCD_ROWS = 4
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)
lcd.backlight_on()
lcd.clear()

# Sensor
sensor = dht.DHT11(Pin(4))

# RGB LED
redLED = PWM(Pin(16))
greenLED = PWM(Pin(17))
blueLED = PWM(Pin(18))
for led in [redLED, greenLED, blueLED]:
    led.freq(1000)
    led.duty_u16(0)

# Buzzer
buzzer = Pin(5, Pin.OUT)

# WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while not wlan.isconnected():
    time.sleep(1)

# HTTP server
addr = socket.getaddrinfo('0.0.0.0', 12345)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print("Server pornit la:", wlan.ifconfig()[0])

def set_rgb(r, g, b):
    redLED.duty_u16(int(r * 65535))
    greenLED.duty_u16(int(g * 65535))
    blueLED.duty_u16(int(b * 65535))

def actualizeaza_afisaj(temp, humidity):
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.print("Temperatura: {} C".format(temp))
    lcd.set_cursor(0, 1)
    lcd.print("Umiditate: {} %".format(humidity))

    if temp > 30:
        lcd.set_cursor(0, 2)
        lcd.print("Canicula 🔆")
        buzzer.on()
        time.sleep(1)
        buzzer.off()
    elif temp < 0:
        lcd.set_cursor(0, 2)
        lcd.print("Ger ❄")
        buzzer.on()
        time.sleep(1)
        buzzer.off()
    else:
        lcd.set_cursor(0, 2)
        lcd.print("Normal 🌤")

try:
    sensor.measure()
    #temp = sensor.temperature()
    temp=-5
    humidity = sensor.humidity()

    r, g, b = h2RGB.getRGB(temp * 3)
    set_rgb(r, g, b)

    actualizeaza_afisaj(temp, humidity)

except Exception as e:
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.print("Eroare senzor")

while True:
    client, addr = s.accept()
    request = client.recv(1024).decode()
    print("Cerere de la:", addr)

    temp = "-"
    humidity = "-"

    if '/temp' in request or '/humidity' in request or '/' in request:
        try:
            sensor.measure()
            temp = sensor.temperature()
            humidity = sensor.humidity()

            r, g, b = h2RGB.getRGB(temp * 3)
            set_rgb(r, g, b)

            actualizeaza_afisaj(temp, humidity)

        except Exception as e:
            temp = "Err"
            humidity = "Err"
            lcd.clear()
            lcd.set_cursor(0, 0)
            lcd.print("Eroare senzor")

        response = """\
HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n
<!DOCTYPE html>
<html>
<head>
    <title>Statie meteo</title>
    <style>
        body {{ font-family: Arial; text-align: center; margin-top: 50px; }}
        h1 {{ color: #4CAF50; }}
        button {{
            background-color: #4CAF50; color: white;
            padding: 10px 20px; font-size: 16px;
            border: none; border-radius: 5px;
            cursor: pointer; margin: 5px;
        }}
        button:hover {{ background-color: #45a049; }}
    </style>
</head>
<body>
    <h1>Statie Meteo</h1>
    <p><strong>Temperatura:</strong> {} &deg;C</p>
    <p><strong>Umiditate:</strong> {} %</p>
    <form action="/temp"><button>Actualizeaza temperatura</button></form>
    <form action="/humidity"><button>Actualizeaza umiditate</button></form>
</body>
</html>
""".format(temp, humidity)

        client.send(response)
        client.close()
