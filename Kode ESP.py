from machine import Pin, SoftI2C
import ssd1306
import machine
import time
import network
import dht
import urequests

i2c = SoftI2C(scl=Pin(32), sda=Pin(33))

devices = i2c.scan()
if not devices:
    print("Error: OLED tidak terdeteksi!")
    oled = None  
    oled_status = 0
else:
    print("OLED terdeteksi!")
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    oled_status = 1

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Menghubungkan ke WiFi", end="")

if oled:
    oled.fill(0)
    oled.text("Menghubungkan WiFi", 0, 20)
    oled.show()

wlan.connect("NAYAYA", "Nayaya 041625")

timeout = 10
while not wlan.isconnected() and timeout > 0:
    print(".", end="")
    time.sleep(1)
    timeout -= 1

print()

if wlan.isconnected():
    print(f"WiFi Terhubung!")
    if oled:
        oled.fill(0)
        oled.text("WiFi Terhubung!", 0, 20)
        oled.show()
else:
    print("Gagal terhubung ke WiFi!")
    if oled:
        oled.fill(0)
        oled.text("Gagal terhubung Wi-Fi!", 0, 20)
        oled.show()

UBIDOTS_ENDPOINT = "https://industrial.api.ubidots.com/api/v1.6/devices/esp-sigma/"
flask_endpoint = "http://192.168.1.11:5002/save"

sensor = dht.DHT11(machine.Pin(25))

while True:
    time.sleep(2)
    sensor.measure()
    suhu = sensor.temperature()
    kelembaban = sensor.humidity()
    print(f"Suhu = {suhu} C, Kelembaban = {kelembaban} %, OLED = {oled_status}")

    if oled:
        oled.fill(0)  
        oled.text(f"Suhu: {suhu}C", 0, 20)
        oled.text(f"Kelembaban: {kelembaban}%", 0, 40)
        oled.show()

    data = {
        "suhu": suhu,
        "kelembaban": kelembaban,
        "oled_status": oled_status
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": "BBUS-O7RXmFm92gxWVuocuMAXWtybjjEGsC"
    }

    try:
        response = urequests.post(UBIDOTS_ENDPOINT, json=data, headers=headers)
        print(f"Respon Ubidots: {response.status_code}")
        response.close()
    except:
        print("Gagal mengirim ke Ubidots")

    headers = {"Content-Type": "application/json"}
    
    try:
        response = urequests.post(flask_endpoint, json=data, headers=headers)
        print(f"Respon Flask (MongoDB): {response.status_code}")
        response.close()
    except:
        print("Gagal mengirim ke Flask (MongoDB)")

    time.sleep(5) 

