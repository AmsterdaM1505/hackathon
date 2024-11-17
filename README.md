# GeoApp

GeoApp — это плагин для мобильного приложения на основе Python, созданное с использованием Kivy, которое отслеживает геолокацию пользователя с помощью GPS и предоставляет информацию о близлежащих компаниях на основе их координат. Приложение отображает уведомление, если в радиусе 1 км найдена какая-либо компания, показывая сведения о компании и изображение (если доступно). Логика на стороне сервера обрабатывается API на основе Flask, который взаимодействует с базой данных MySQL.
## Features

- **GPS Tracking**: приложение может отслеживать местоположение пользователя с помощью GPS устройства или эмулированных данных.
- **Уведомления о компаниях поблизости**: отправляет уведомление с информацией о компаниях поблизости в радиусе 1 км.
- **Декодирование изображений Base64**: декодирует изображения из формата Base64 и отображает их в приложении.
- **Навигация по ссылкам**: позволяет пользователям переходить на веб-сайт компании с помощью кнопки.
- **Сервер Flask**: сервер извлекает данные из базы данных MySQL и возвращает соответствующие компании на основе местоположения пользователя.

## Prerequisites

### Python Libraries

Приложение использует следующие библиотеки:

- `kivy`
- `plyer` (for GPS tracking)
- `mysql-connector-python` (for database interaction)
- `flask` (for server-side handling)
- `requests`
- `webbrowser`
- `base64`
- `io`

### MySQL Database

Убедитесь, что у вас настроена база данных MySQL с таблицей `companies`, содержащей следующие поля:

- `id` (INT)
- `Company_name` (VARCHAR)
- `x_coordinate` (FLOAT)
- `y_coordinate` (FLOAT)
- `advertising` (TEXT, storing Base64 encoded image)
- `link` (VARCHAR)

### Database Connection Setup

Измените файл `server.py`, включив в него данные о подключении к базе данных MySQL:

```python
def get_db_connection():
    return mysql.connector.connect(
        host='your_host',
        user='your_username',
        password='your_password',
        database='your_database'
    )
```

## Installation
### Клонируйте репозиторий:
```bash
git clone https://github.com/AmsterdaM1505/hackathon.git
```
### Измените свою базу данных или же импортируйте competition.sql
### Запуск установки через setup.py
```bash
python setup.py install
```
### Запуск тестового приложения
```bash
python server.py
python example_app.py
```
### В случае проблем проверьте скачан ли kivy
```bash
pip install kivy
```
### Рекомендуемые средства
[PyCharm](https://www.jetbrains.com/ru-ru/pycharm/)
[Wampserver](https://www.wampserver.com/)
