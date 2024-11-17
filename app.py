from plyer import gps
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.graphics import Color, Ellipse, RoundedRectangle
import random
import requests
from kivy.uix.image import Image
from kivy.uix.button import Button
import webbrowser
import base64
from pathlib import Path
import os

# window correction
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '100')
Config.set('graphics', 'left', '200')
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'fullscreen', '0')

# Creation button for the settings
class SwitchButton(Widget):
    is_on = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()
        self.bind(on_touch_down=self.on_touch_down)
        self.ellipse_bg = None
        self.circle = None

    def on_touch_down(self, touch, *args):
        if self.collide_point(*touch.pos):
            self.is_on = not self.is_on
            self.update_canvas()
            return True
        return super().on_touch_down(touch)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.8, 0.8, 0.8) if not self.is_on else Color(0.3, 0.7, 0.3)
            self.ellipse_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[(self.height / 2,)] * 4)
            circle_x = self.x + (self.width - self.height) if self.is_on else self.x
            Color(1, 1, 1)
            self.circle = Ellipse(pos=(circle_x, self.y), size=(self.height, self.height))

# main class
class GeoApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.cursor = None
        self.switch_button = None
        self.layout = None
        self.label = None

    # interface building
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.label = Label(text="Ожидание данных геолокации...")
        self.layout.add_widget(self.label)

        self.switch_button = SwitchButton(size_hint=(None, None), size=(100, 50))
        self.layout.add_widget(self.switch_button)
        self.switch_button.bind(is_on=self.on_switch)

        return self.layout

    def on_switch(self, instance, value):
        if value:
            self.start_gps()
        else:
            self.stop_gps()

    def start_gps(self):
        try:
            gps.start(minTime=1000, minDistance=1)
            self.label.text = "GPS запущен. Ожидание данных..."
        except Exception as e:
            try:
                gps.configure(on_location=self.on_location, on_status=self.on_status)
            except NotImplementedError:
                self.label.text = "GPS не поддерживается на этом устройстве. Используется эмуляция."
                self.emulate_location()

    def stop_gps(self):
        try:
            gps.stop()
            self.label.text = "GPS остановлен."
        except Exception as e:
            error_message = "GPS остановлен."
            print(error_message)  # Для отладки
            self.label.text = error_message

    # получение координат
    def on_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        self.label.text = f"Широта: {lat}\nДолгота: {lon}"
        self.check_nearby_companies(lat, lon)

    def check_nearby_companies(self, user_lat, user_lon):
        try:
            response = requests.get('http://localhost:5000/nearby_companies', params={'lat': user_lat, 'lon': user_lon})

            if response.status_code == 200:
                results = response.json()
                help_res = random.choice(results)
                company_name = help_res.get('Company_name')
                advert = help_res.get('advertising')
                link = help_res.get('link')
                distance = help_res.get('distance')
                if results:
                    self.show_popup4(help_res, company_name, distance, advert, link)
                    if os.path.exists("temp_image.jpg"):
                        try:
                            os.remove("temp_image.jpg")
                        except Exception as e:
                            print(f"Ошибка при удалении файла: {e}")
                else:
                    self.show_popup("Нет организаций в радиусе 1 км.")
            else:
                self.label.text = "Ошибка при запросе данных с сервера"
        except Exception as e:
            print(f"Ошибка выполнения HTTP-запроса: {e}")
            self.label.text = "Ошибка выполнения HTTP-запроса к серверу"

    def on_status(self, stype, status):
        self.label.text = f"Статус: {status}"

    # создает фиктивные данные о местонахождении пользователя
    def emulate_location(self):
        fake_data = {'lat': 55.7332, 'lon': 37.7478}
        self.on_location(**fake_data)

    def show_popup(self, message, company_name, distance, advert, link):
        if isinstance(message, str):
            content = message
        else:
            content = "Неверный формат сообщения"

        popup = Popup(title='Уведомление',
                      content=Label(text=content),
                      size_hint=(0.8, 0.4))
        popup.open()

    def decode_image_from_base64(self, encoded_string, output_path):
        image_data = base64.b64decode(encoded_string)
        with open(output_path, "wb") as output_file:
            # Запись бинарных данных обратно в файл
            output_file.write(image_data)

    def show_popup4(self, message, company_name, distance, advertising, link):
        # Функция для исправления недостатка заполнения Base64
        def fix_base64_padding(data):
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            return data

        # Декодируем закодированное изображение из Base64
        image = None
        # Декодируем закодированное изображение из Base64
        try:
            if advertising:
                advertising = fix_base64_padding(advertising)
                image_data = base64.b64decode(advertising)
                try:
                    with open("temp_image.jpg", "wb") as img_file:
                        img_file.write(image_data)
                except Exception as e:
                    print(f"Ошибка с временным файлом изображения: {e}")
        except Exception as e:
            print(f"Ошибка декодирования изображения 1: {e}, ", image)
            image = None

        # Создание основной компоновки для всплывающего окна
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Добавление названия компании и расстояния
        if company_name and distance is not None:
            info_label = Label(text=f"Совсем рядом {str(company_name)}\nнужно пройти всего лишь {str(round(distance, 2))} км",
                               size_hint_y=None, height=60)
            layout.add_widget(info_label)

        # Добавление изображения, если оно существует
        if image:
            img_widget = Image(texture=image.texture, size_hint_y=None, height=200)
            layout.add_widget(img_widget)

        if Path("temp_image.jpg").is_file():
            img_widget = Image(source="temp_image.jpg")
            layout.add_widget(img_widget)

        # Кнопка для перехода по ссылке
        def open_link(instance):
            if link:
                webbrowser.open(link)

        # Кнопка для перехода по ссылке
        link_button = Button(text="Посетить сайт", height=20)
        link_button.bind(on_release=open_link)
        layout.add_widget(link_button)

        # Кнопка закрытия всплывающего окна
        close_button = Button(text="Закрыть", height=20)
        close_button.bind(on_release=lambda x: popup.dismiss())
        layout.add_widget(close_button)

        # Создание и отображение всплывающего окна с меньшей высотой
        popup = Popup(title="Информация об организации", content=layout, size_hint=(0.6, 0.5))  # Ширина 60%, высота 50%
        popup.open()


if __name__ == '__main__':
    GeoApp().run()