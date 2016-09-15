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
from kivy.properties import ObjectProperty, StringProperty
from jukebar import run_jukebar

class MainScreen(Screen):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''

    def on_settings_action(self):
        print "open settings"

    def start_juke_action(self):
        print "start_juke_action called!"
        run_jukebar()
        print "start_juke_action end"

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