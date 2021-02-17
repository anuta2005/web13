import requests
import sys
import pygame
import os
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт

from PIL import Image
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QWidget

api_server = "http://static-maps.yandex.ru/1.x/"

lon = "37.530887"
t = lon
lat = "55.703118"
delta = "0.002"
response1 = None
k1 = delta
k = "map"
f = False
organ = str()

def find(toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.005"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "l": "map",
        "pt": ",".join([toponym_longitude, toponym_lattitude])
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    return response

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Поиск организации')

        self.btn = QPushButton('Искать', self)
        self.btn.resize(self.btn.sizeHint())
        self.btn.move(100, 150)
        self.btn.clicked.connect(self.hello)


        self.name_input = QLineEdit(self)
        self.name_input.move(80, 90)

    def hello(self):
        name = self.name_input.text()
        global organ
        organ = name
        self.close()




pygame.init()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        key = pygame.key.get_pressed()
        if key[pygame.K_PLUS]:
            if delta < "3":
                delta = str(float(delta) + 0.001)
        if key[pygame.K_MINUS]:
            if delta > "0.001":
                delta = str(float(delta) - 0.001)
        if key[pygame.K_LEFT]:
            if float(lon) > float(k1) - 0.01:
                lon = str(float(lon) - 0.0001)
        if key[pygame.K_RIGHT]:
            if float(lon) < float(k1) + 0.01:
                lon = str(float(lon) + 0.0001)
        if key[pygame.K_UP]:
            if float(lat) < float(t) + 0.01:
                lat = str(float(lat) + 0.0001)
        if key[pygame.K_DOWN]:
            if float(lat) > float(t) - 0.01:
                lat = str(float(lat) - 0.0001)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if 0 < pos[0] < 20 and 0 < pos[1] < 20:
                k = "map"
            if 20 < pos[0] < 40 and 0 < pos[1] < 20:
                k = "sat"
            if 40 < pos[0] < 60 and 0 < pos[1] < 20:
                k = "sat,skl"
            if 5 < pos[0] < 100 and 20 < pos[1] < 30:
                app = QApplication(sys.argv)
                ex = Example()
                ex.show()
                app.exec()
                response1 = find(organ)


    params = {
        "ll": ",".join([lon, lat]),
        "spn": ",".join([delta, delta]),
        "l": k
    }

    response = requests.get(api_server, params=params)
    if response1:
        response = response1
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(map_file), (0, 0))


    font0 = pygame.font.Font(None, 20)  # слова вверху
    text0 = font0.render("Сх", True, (0, 0, 0))
    screen.blit(text0, (10, 0))
    text1 = font0.render("Сп", True, (0, 0, 0))
    screen.blit(text1, (30, 0))
    text2 = font0.render("Г", True, (0, 0, 0))
    screen.blit(text2, (50, 0))

    font = pygame.font.Font(None, 25)
    text2 = font.render("ИСКАТЬ", True, (0, 0, 0))
    screen.blit(text2, (5, 20))

    pygame.display.flip()
pygame.quit()

os.remove(map_file)
