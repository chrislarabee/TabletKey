import time

import pyautogui as pg
from kivy.app import App
from kivy.properties import (ListProperty, BooleanProperty, ObjectProperty, StringProperty)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


class Keybind(Button):
    bound_key_text = StringProperty('')
    bound_keys = ListProperty([])
    tab_back = BooleanProperty(False)

    def setup(self, binding: str):
        self.bound_key_text = binding
        self.bound_keys = binding.split('+')

    def send(self):
        pg.hotkey('alt', 'tab')
        time.sleep(0.1)
        pg.hotkey(*self.bound_keys)
        if self.tab_back:
            time.sleep(0.1)
            pg.hotkey('alt', 'tab')

    def on_bound_key_text(self, *args):
        self.text = self.bound_key_text


class NewBindDialogue(AnchorLayout):
    bind_input = ObjectProperty(None)
    bind_text = StringProperty('')

    def update_bind(self, text: str = ''):
        self.bind_text = text

    def cancel(self):
        self.parent.remove_widget(self)

    def commit(self):
        new_btn = Keybind()
        new_btn.setup(self.bind_text)
        self.parent.btn_layout.add_widget(new_btn)
        self.parent.remove_widget(self)


class AppFrame(FloatLayout):
    btn_layout = ObjectProperty(None)

    def new_keybind_dialogue(self):
        nbd = NewBindDialogue()
        self.add_widget(nbd)

    def new_keybind(self, bind_text, **options):
        pass


class TabletKeyApp(App):
    def build(self):
        return AppFrame()


if __name__ == '__main__':
    TabletKeyApp().run()
