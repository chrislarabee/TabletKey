import json
import os
import time

import pyautogui as pg
from kivy.app import App
import kivy.properties as kp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


class Keybind(Button):
    bound_keys = kp.ListProperty([])
    tab_back = kp.BooleanProperty(False)

    def output(self):
        return dict(
            binding=self.bound_key_text,
            tab_back=self.tab_back
        )

    def setup(self, name: str, binding: str, tab_back: bool = False):
        self.bound_keys = binding.split('+')
        self.tab_back = tab_back
        self.text = name

    def send(self):
        pg.hotkey('alt', 'tab')
        time.sleep(0.1)
        pg.hotkey(*self.bound_keys)
        if self.tab_back:
            time.sleep(0.1)
            pg.hotkey('alt', 'tab')


class NewBindDialogue(AnchorLayout):
    name = kp.StringProperty('')
    binding_props = dict(
        binding='',
        tab_back=False,
    )

    def update_binding_props(self, **props):
        for k, v in props.items():
            self.binding_props[k] = v

    def cancel(self):
        self.parent.remove_widget(self)

    def commit(self):
        self.parent.update_keybind(**self.binding_props)
        self.parent.remove_widget(self)


class NameBindSet(AnchorLayout):
    name_input = kp.ObjectProperty(None)
    mode = kp.StringProperty('Save')

    def cancel(self):
        self.parent.remove_widget(self)

    def commit(self):
        if self.mode == 'Load':
            self.parent.load(self.name_input.text)
        else:
            self.parent.save(self.name_input.text)
        self.parent.remove_widget(self)


class AppFrame(FloatLayout):
    btn_layout = kp.ObjectProperty(None)
    keybindings = kp.DictProperty({})
    config = kp.DictProperty({})

    def new_keybind_dialogue(self):
        nbd = NewBindDialogue()
        self.add_widget(nbd)

    def new_bindset_dialogue(self, mode: str = 'Save'):
        sbs = NameBindSet(mode=mode)
        self.add_widget(sbs)

    def update_keybind(self, **options):
        bind_name = options.get('name')
        if self.keybindings.get(bind_name):
            self.keybindings[bind_name].setup(**options)
        else:
            new_btn = Keybind()
            new_btn.setup(**options)
            self.keybindings[bind_name] = new_btn
            self.btn_layout.add_widget(new_btn)

    @staticmethod
    def to_json(file_path: str, data: dict):
        with open(file_path, 'w') as w:
            w.write(json.dumps(data))

    @staticmethod
    def from_json(file_path: str):
        if os.path.exists(file_path):
            with open(file_path, 'r') as r:
                for line in r:
                    result = json.loads(line)
            return result
        else:
            return dict()

    def save(self, file_name: str):
        result = dict()
        for k, v in self.keybindings.items():
            result[k] = {**v.output()}
        self.to_json(f'bindsets/{file_name}.json', result)
        self.config['last_bindset'] = file_name
        self.save_config()

    def save_config(self):
        self.to_json('ref.json', self.config)

    def load(self, file_name: str):
        p = f'bindsets/{file_name}.json'
        if os.path.exists(p):
            result = self.from_json(p)
            for k, v in result.items():
                b = Keybind()
                b.setup(k, **v)
                self.keybindings[k] = b
                self.btn_layout.add_widget(b)
            return True
        else:
            return False


class TabletKeyApp(App):
    app = kp.ObjectProperty(None)

    def build(self):
        self.app = AppFrame()
        return self.app

    def load_last_bset(self, bset_name: str):
        print(f'Attempting to load the last used bindset {bset_name}...')
        load_result = self.app.load(bset_name)
        if load_result:
            print(f'Load of {bset_name}.json successful.')
        else:
            self.app.config.pop('last_bindset')
            self.app.save_config()
            print(f'Load failed. bindsets/{bset_name}.json no '
                  f'longer exists.')

    @staticmethod
    def setup_basics():
        if not os.path.exists('bindsets/'):
            os.mkdir('bindsets')

    def on_start(self):
        self.setup_basics()
        self.root_window.borderless = True
        print('Performing TabletKey startup...')
        result = self.app.from_json('ref.json')
        for k, v in result.items():
            self.app.config[k] = v
        last_bset = self.app.config.get('last_bindset')
        if last_bset:
            self.load_last_bset(last_bset)


if __name__ == '__main__':
    TabletKeyApp().run()
