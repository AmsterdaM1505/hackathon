from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from app import GeoApp

class ExampleApp(App):
    def build(self):
        layout = BoxLayout()
        geo_app = GeoApp()
        layout.add_widget(geo_app.build())
        return layout

if __name__ == '__main__':
    ExampleApp().run()
