import time

import pyautogui as pg
from kivy.app import App
from kivy.properties import ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class Keybind(Button):
    bound_keys = ListProperty([])
    tab_back = BooleanProperty(False)

    def send(self):
        pg.hotkey('alt', 'tab')
        time.sleep(0.1)
        pg.hotkey(*self.bound_keys)
        time.sleep(0.1)
        if self.tab_back:
            pg.hotkey('alt', 'tab')


class AppFrame(BoxLayout):
    pass


class TabletKeyApp(App):
    def build(self):
        return AppFrame()


if __name__ == '__main__':
    TabletKeyApp().run()
