import os
from os.path import expanduser
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from jukebar import JukebarThread


JSON_STORE_PATH = "config.json"


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

    def get_cut_songs(self):
        setting_screen = self.get_setting_screen()
        cut_songs_property = setting_screen.cut_songs_property
        return cut_songs_property

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
        cut_songs = self.get_cut_songs()
        min_sleep_time = self.get_timer_min_value()
        max_sleep_time = self.get_timer_max_value()
        self.jukebar_thread = JukebarThread(
            musics=cut_songs,
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


class LoadDialog(FloatLayout):
    path = StringProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SettingScreen(Screen):
    timer_min_property = ObjectProperty()
    timer_max_property = ObjectProperty()
    cut_songs_property = ListProperty([])

    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)
        json_store_path = App.get_running_app().json_store_path
        self.store = JsonStore(json_store_path)
        self.update_cut_songs_list_view()

    def cut_songs(self):
        """
        Returns the current interruption songs list (full path).
        """
        try:
            songs = self.store.get('cut_songs')['list']
        except KeyError:
            songs = []
        return songs

    def show_load(self):
        home = expanduser("~")
        content = LoadDialog(
            load=self.load, cancel=self.dismiss_popup, path=home)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def update_cut_songs_list_view(self):
        """
        Updates the ListView with the current cut songs list.
        """
        self.cut_songs_property = self.cut_songs()

    def load(self, path, filename):
        cut_songs = self.cut_songs()
        cut_songs.extend(filename)
        self.store.put('cut_songs', list=cut_songs)
        self.update_cut_songs_list_view()
        self.dismiss_popup()


class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    pass


class ControllerApp(App):

    def build(self):
        return Controller()

    @property
    def json_store_path(self):
        """
        Returns the JSON store file path.
        """
        return os.path.join(self.user_data_dir, JSON_STORE_PATH)

if __name__ == '__main__':
    ControllerApp().run()
