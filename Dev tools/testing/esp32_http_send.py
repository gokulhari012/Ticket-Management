import requests
esp32_ip = "http://192.168.0.100/send"  # Change to your ESP32 IP
data = {"message": "ggg"}
response = requests.get(esp32_ip, params=data)
print(response.text)


