import json
import time

import pyautogui as pg
from kivy.app import App
from kivy.properties import (
    ListProperty, BooleanProperty, ObjectProperty, StringProperty, DictProperty)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


class Keybind(Button):
    bound_key_text = StringProperty('')
    bound_keys = ListProperty([])
    tab_back = BooleanProperty(False)

    def output(self):
        return dict(
            tab_back=self.tab_back
        )

    def setup(self, binding: str, **options):
        self.bound_key_text = binding
        self.bound_keys = binding.split('+')
        self.tab_back = options.get('tab_back', False)
        self.text = '+'.join([b.capitalize() for b in self.bound_keys])

    def send(self):
        pg.hotkey('alt', 'tab')
        time.sleep(0.1)
        pg.hotkey(*self.bound_keys)
        if self.tab_back:
            time.sleep(0.1)
            pg.hotkey('alt', 'tab')


class NewBindDialogue(AnchorLayout):
    bind_input = ObjectProperty(None)
    bind_text = StringProperty('')
    tab_back = BooleanProperty(False)

    def update_bind(self, text: str = ''):
        self.bind_text = text

    def cancel(self):
        self.parent.remove_widget(self)

    def commit(self):
        self.parent.update_keybind(self.bind_text, **self.__dict__)
        self.parent.remove_widget(self)


class NameBindSet(AnchorLayout):
    name_input = ObjectProperty(None)
    mode = StringProperty('Save')

    def cancel(self):
        self.parent.remove_widget(self)

    def commit(self):
        if self.mode == 'Load':
            self.parent.load(self.name_input.text)
        else:
            self.parent.save(self.name_input.text)
        self.parent.remove_widget(self)


class AppFrame(FloatLayout):
    btn_layout = ObjectProperty(None)
    keybindings = DictProperty({})

    def new_keybind_dialogue(self):
        nbd = NewBindDialogue()
        self.add_widget(nbd)

    def new_bindset_dialogue(self, mode: str = 'Save'):
        sbs = NameBindSet(mode=mode)
        self.add_widget(sbs)

    def update_keybind(self, bind_text: str, **options):
        if self.keybindings.get(bind_text):
            self.keybindings[bind_text].setup(bind_text, **options)
        else:
            new_btn = Keybind()
            new_btn.setup(bind_text, **options)
            self.keybindings[bind_text] = new_btn
            self.btn_layout.add_widget(new_btn)

    def save(self, file_name: str):
        result = dict()
        for k, v in self.keybindings.items():
            result[k] = {**v.output()}
        with open(f'bindsets/{file_name}.json', 'w') as w:
            w.write(json.dumps(result))

    def load(self, file_name: str):
        with open(f'bindsets/{file_name}.json', 'r') as r:
            for line in r:
                result = json.loads(line)
            for k, v in result.items():
                b = Keybind()
                b.setup(k, **v)
                self.keybindings[k] = b
                self.btn_layout.add_widget(b)




class TabletKeyApp(App):
    def build(self):
        return AppFrame()


if __name__ == '__main__':
    TabletKeyApp().run()
