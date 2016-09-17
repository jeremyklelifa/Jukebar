"""
Go to your project properties, either by right-clicking on the project and picking "Properties" or by picking Properties from the Project menu.
Click on Debug, then enter your arguments into the "Script Arguments" field.
Save.
-m screen:onex,portrait,scale=.75
"""

import kivy
kivy.require('1.9.1')

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import ObjectProperty
from jukebar import JukebarThread

class MainScreen(Screen):
    toggle_juke_property = ObjectProperty()
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.jukebar_thread = None

    def on_settings_action(self):
        print "open settings"

    def get_setting_screen(self):
        screen_manager = self.parent
        controller = screen_manager.parent
        setting_screen = controller.ids['setting_screen_id']
        return setting_screen

    def get_timer_min_value(self):
        setting_screen = self.get_setting_screen()
        timer_min_property = setting_screen.timer_min_property
        timer_min_text = timer_min_property.text
        timer_min_value = int(timer_min_text)
        return timer_min_value

    def get_timer_max_value(self):
        setting_screen = self.get_setting_screen()
        timer_max_property = setting_screen.timer_max_property
        timer_max_text = timer_max_property.text
        timer_max_value = int(timer_max_text)
        return timer_max_value

    def start_juke_action(self):
        min_sleep_time = self.get_timer_min_value()
        max_sleep_time = self.get_timer_max_value()
        self.jukebar_thread = JukebarThread(
            min_sleep_time=min_sleep_time,
            max_sleep_time=max_sleep_time,
        )
        self.jukebar_thread.start()

    def stop_juke_action(self):
        if self.jukebar_thread is None:
            return
        self.jukebar_thread.stop()
        self.jukebar_thread.join()

    def toggle_juke_action(self):
        toggle_juke_property = self.toggle_juke_property
        if toggle_juke_property.state == 'down':
            self.start_juke_action()
            toggle_juke_property.text = "Stop Juke"
        else:
            self.stop_juke_action()
            toggle_juke_property.text = "Start Juke"

class SettingScreen(Screen):
    timer_min_property = ObjectProperty()
    timer_max_property = ObjectProperty()

class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    pass


class ControllerApp(App):

    def build(self):
        return Controller()

if __name__ == '__main__':
    ControllerApp().run()
