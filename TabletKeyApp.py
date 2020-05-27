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
    """
    Stores keybindings and manages actually sending them out of
    TabletKeyApp and to the next window.
    """
    bound_keys = kp.ListProperty([])
    tab_back = kp.BooleanProperty(False)
    position = kp.ListProperty([0, 0])

    def output(self) -> dict:
        """

        :return: A dictionary containing the vital binding properties
            of the Keybind so that they can be saved.
        """
        return dict(
            position=self.pos,
            binding='+'.join(self.bound_keys),
            tab_back=self.tab_back
        )

    def setup(self, name: str, binding: str, position: (list, tuple) = None,
              tab_back: bool = False) -> None:
        """
        Sets a Keybind button up, or overwrites the existing properties
        if used on an existing Keybind object.

        :param name: A string, the user-supplied name of the keybinding
            to display on the button.
        :param binding: A string with each keyboard key separated by a
            plus (+) sign.
        :param position: A list or tuple, currently mostly a
            placeholder for when user-specified Keybind button
            placement is implemented.
        :param tab_back: A boolean, indicates whether, when this
            Keybind is pressed, the user wants to immediately tab back
            to the TabletKeyApp window.
        :return: None
        """
        self.bound_keys = binding.split('+')
        self.tab_back = tab_back
        self.position = position if position is not None else [0, 0]
        self.text = name

    def send(self) -> None:
        """
        Uses pyautogui to send the contents of the Keybind to the next
        window.

        :return: None
        """
        pg.hotkey('alt', 'tab')
        # A slight delay is necessary to successfully input the
        # keystroke into the other window.
        time.sleep(0.1)
        pg.hotkey(*self.bound_keys)
        if self.tab_back:
            time.sleep(0.1)
            pg.hotkey('alt', 'tab')


class InputWindow(AnchorLayout):
    """
    A parent class for AnchorLayout Widgets that have a pop-up window
    functionality.
    """
    def execute(self) -> None:
        """
        Override this method in inheritance to customize what the
        InputWindow object does on commit.

        :return: None
        """
        pass

    def cancel(self) -> None:
        """
        Closes the InputWindow widget.

        :return: None
        """
        self.parent.remove_widget(self)

    def commit(self) -> None:
        """
        Executes whatever functionality is assigned to the InputWindow
        widget and then closes the InputWindow widget.

        :return None:
        """
        self.execute()
        self.parent.remove_widget(self)


class NewBinding(InputWindow):
    """
    Acts as a user-friendly gui for creating new Keybind objects.
    """
    name = kp.StringProperty('')
    binding_props = dict(
        binding='',
        tab_back=False,
    )

    def update_binding_props(self, **props) -> None:
        """
        A universal method for updating the contents of binding_props
        using kwargs.

        :param props: Any number of kwargs.
        :return: None
        """
        for k, v in props.items():
            self.binding_props[k] = v

    def execute(self) -> None:
        """
        Sends binding_props off to parent (AppFrame expected) to create
        a new Keybind.

        :return: None
        """
        self.parent.update_keybind(**self.binding_props)


class NameBindSet(InputWindow):
    """
    A simple text input for collecting user input when saving or
    loading bindset json files.
    """
    name_input = kp.ObjectProperty(None)
    mode = kp.StringProperty('Save')

    def execute(self) -> None:
        """
        Instructs parent (expects AppFrame) to save or load the user-
        specified file name in name_input.

        :return None:
        """
        if self.mode == 'Load':
            self.parent.load(self.name_input.text)
        else:
            self.parent.save(self.name_input.text)


class AppFrame(FloatLayout):
    """
    The core layout of the application, acts as the root widget and
    provides methods universal to all child widgets.
    """
    btn_layout = kp.ObjectProperty(None)
    keybindings = kp.DictProperty({})
    config = kp.DictProperty({})

    def new_keybind_dialogue(self) -> None:
        """
        Opens a NewBindDialogue pop up to get user input.

        :return: None
        """
        nbd = NewBinding()
        self.add_widget(nbd)

    def name_bindset_dialogue(self, mode: str = 'Save') -> None:
        """
        Opens a NameBindSet pop up to get user input.

        :param mode: A string, either 'Save' or 'Load'.
        :return: None
        """
        sbs = NameBindSet(mode=mode)
        self.add_widget(sbs)

    def update_keybind(self, **options) -> None:
        """
        Creates a new Keybind object or updates an existing one.

        :param options: kwargs. Main kwarg that update_keybind requires
            is name, a string specifying the user-supplied name of the
            keybind.
        :return: None
        """
        bind_name = options.get('name')
        if self.keybindings.get(bind_name):
            self.keybindings[bind_name].setup(**options)
        else:
            new_btn = Keybind()
            new_btn.setup(**options)
            self.keybindings[bind_name] = new_btn
            self.btn_layout.add_widget(new_btn)

    @staticmethod
    def to_json(file_path: str, data: dict) -> None:
        """
        Simple method to save a one line dictionary to a json file.

        :param file_path: A string, a valid file path.
        :param data: A dictionary.
        :return: None
        """
        with open(file_path, 'w') as w:
            w.write(json.dumps(data))

    @staticmethod
    def from_json(file_path: str) -> dict:
        """
        Simple method to load a one line json into a python dictionary.

        :param file_path: A string, a file path.
        :return: A dictionary containing the json in file_path, or an
            empty dictionary if the file_path was invalid.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r') as r:
                for line in r:
                    result = json.loads(line)
            return result
        else:
            return dict()

    def save(self, file_name: str) -> None:
        """
        Saves all the Keybinds in keybindings as well as the values
        stored in config.

        :param file_name: A string, the name of the file to save to.
        :return: None
        """
        result = dict()
        for k, v in self.keybindings.items():
            result[k] = {**v.output()}
        self.to_json(f'bindsets/{file_name}.json', result)
        self.config['last_bindset'] = file_name
        self.save_config()

    def save_config(self) -> None:
        """
        Saves the config dictionary to a json file called ref.

        :return: None
        """
        self.to_json('ref.json', self.config)

    def load(self, file_name: str) -> bool:
        """
        Loads a specified bindset from the bindsets directory and
        replaces the existing bindset with Keybinds corresponding to
        the new bindset.

        :param file_name: A valid file path.
        :return: A boolean indicating whether data was successfully
            retrieved from the passed file.
        """
        p = f'bindsets/{file_name}.json'
        result = self.from_json(p)
        if len(result) > 0:
            self.btn_layout.clear_widgets()
            for k, v in result.items():
                b = Keybind()
                b.setup(k, **v)
                self.keybindings[k] = b
                self.btn_layout.add_widget(b)
            return True
        else:
            return False


class TabletKeyApp(App):
    """
    The core app of TabletKeyApp.
    """
    app = kp.ObjectProperty(None)

    def build(self) -> AppFrame:
        """
        Builds the widget tree based on tabletkey.kv.

        :return: An AppFrame object.
        """
        self.app = AppFrame()
        return self.app

    def load_last_bset(self, bset_name: str) -> None:
        """
        If TabletKeyApp has been run before, this method will
        automatically load the last bindset file into the window.

        :param bset_name: A string, a file name found in bindsets.
        :return: None
        """
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
    def setup_basics() -> None:
        """
        Simple method to ensure that the expected file structure is in
        place.

        :return: None
        """
        if not os.path.exists('bindsets/'):
            os.mkdir('bindsets')

    def on_start(self) -> None:
        """
        A collection of methods to run and properties to change after
        build.

        :return: None
        """
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
