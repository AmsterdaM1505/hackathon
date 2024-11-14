# тута мы импортируем библиотеки
from plyer import gps
from plyer import notification
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.graphics import Color, Ellipse, RoundedRectangle
import mysql.connector
import random
from threading import Timer
import math

# тута делаем чтобы мой монитор не колбасило
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '100')
Config.set('graphics', 'left', '200')
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'fullscreen', '0')

# здесь делается кнопка
class SwitchButton(Widget):
    is_on = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()
        self.bind(on_touch_down=self.on_touch_down)

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


# основной класс
class GeoApp(App):

    # создаем основной интерфейс
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.label = Label(text="Ожидание данных геолокации...")
        self.layout.add_widget(self.label)

        self.switch_button = SwitchButton(size_hint=(None, None), size=(100, 50))
        self.layout.add_widget(self.switch_button)
        self.switch_button.bind(is_on=self.on_switch)

        return self.layout

    # подключается gps и база данных
    def on_start(self):
        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
        except NotImplementedError:
            self.label.text = "GPS не поддерживается на этом устройстве. Используется эмуляция."
            self.emulate_location()

        # Подключение к базе данных
        self.connect_to_db()

    # связь с бд
    def connect_to_db(self):
        try:
            self.db = mysql.connector.connect(
                host='localhost',
                user='root',
                password='php2023_egorius',
                database='competition'
            )
            self.cursor = self.db.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Ошибка подключения к базе данных: {err}")
            self.label.text = "Ошибка подключения к базе данных"

    # в зависимости от значения кнопки запускается либо старт, либо стоп
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
            error_message = f"Ошибка запуска GPS: {e}"
            print(error_message)  # Для отладки, чтобы видеть ошибку в консоли
            self.label.text = error_message

    def stop_gps(self):
        try:
            gps.stop()
            self.label.text = "GPS остановлен."
        except Exception as e:
            error_message = f"Ошибка остановки GPS: {e}"
            print(error_message)  # Для отладки
            self.label.text = error_message

    # получение координат
    def on_location(self, **kwargs):
        lat = kwargs.get('lat', 'Неизвестно')
        lon = kwargs.get('lon', 'Неизвестно')
        self.label.text = f"Широта: {lat}\nДолгота: {lon}"
        self.check_nearby_companies(lat, lon)

    # проверяет компании в километровом радиусе
    def check_nearby_companies(self, user_lat, user_lon):
        try:
            query = """
                SELECT id, Company_name, x_coordinate, y_coordinate, advertising, 
                (6371 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(x_coordinate)) * 
                COS(RADIANS(y_coordinate) - RADIANS(%s)) + 
                SIN(RADIANS(%s)) * SIN(RADIANS(x_coordinate)))) AS distance
                FROM companies
                HAVING distance <= 1
                ORDER BY distance;
            """
            self.cursor.execute(query, (user_lat, user_lon, user_lat))
            results = self.cursor.fetchall()

            if results:
                chosen_company = random.choice(results)
                self.send_notification(chosen_company)
            else:
                self.show_popup("Нет организаций в радиусе 1 км.")
        except mysql.connector.Error as err:
            print(f"Ошибка выполнения запроса: {err}")
            self.label.text = "Ошибка выполнения запроса к базе данных"

    # создает уведомление
    def send_notification(self, company):
        company_name = company['Company_name']
        advertising = company.get('advertising', None)

        if advertising:
            message = advertising
        else:
            message = f"Хотите посетить {company_name}?"

        notification.notify(
            title="Организация поблизости!",
            message=message,
            timeout=10
        )
        self.show_popup(f"Организация: {company_name}\n{message}")

    def on_status(self, stype, status):
        self.label.text = f"Статус: {status}"

    # остановка приложения по сути
    def on_stop(self):
        try:
            gps.stop()
        except Exception as e:
            print(f"Ошибка остановки GPS при выходе: {e}")

        if hasattr(self, 'db') and self.db.is_connected():
            self.cursor.close()
            self.db.close()

    # создает фиктивные данные о местонахождении пользователя
    def emulate_location(self):
        def mock_data():
            fake_data = {'lat': 55.7558, 'lon': 37.6176}
            self.on_location(**fake_data)

        Timer(5.0, mock_data).start()

    # Показывает текст
    def show_popup(self, message):
        popup = Popup(title='Уведомление',
                      content=Label(text=message),
                      size_hint=(0.8, 0.4))
        popup.open()


if __name__ == '__main__':
    GeoApp().run()
