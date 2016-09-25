import os
from os.path import expanduser
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.theming import ThemeManager
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

    def get_timer_min_value(self):
        app = App.get_running_app()
        timer_min_value = app.timer_min()
        return timer_min_value

    def get_timer_max_value(self):
        app = App.get_running_app()
        timer_max_value = app.timer_max()
        return timer_max_value

    def start_juke_action(self):
        app = App.get_running_app()
        cut_songs = app.cut_songs()
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

    def toggle_juke_action(self, button):
        action_start = button.text == "Start Juke"
        if action_start:
            self.start_juke_action()
            button.text = "Stop Juke"
        else:
            self.stop_juke_action()
            button.text = "Start Juke"


class LoadDialog(FloatLayout):
    path = StringProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SettingScreen(Screen):
    timer_max_property = ObjectProperty()
    timer_min_property = ObjectProperty()
    cut_songs_property = ListProperty([])
    cut_songs_lv_property = ObjectProperty()

    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)
        self.update_cut_songs_list_view()

    def on_timer_min_changed(self):
        self.store.put('timer_max', value=self.timer_min_property.text)

    def on_timer_max_changed(self):
        self.store.put('timer_max', value=self.timer_max_property.text)

    def show_load(self):
        home = expanduser("~")
        content = LoadDialog(
            load=self.load, cancel=self.dismiss_popup, path=home)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def delete_music(self):
        adapter = self.cut_songs_lv_property.adapter
        selection = adapter.selection
        if selection:
            selection_text = selection[0].text
            # adapter.data.remove(selection_text)
            # self.cut_songs_lv_property._trigger_reset_populate()
            cut_songs = self.cut_songs()
            cut_songs.remove(selection_text)
            self.store.put('cut_songs', list=cut_songs)
            self.update_cut_songs_list_view()

    def dismiss_popup(self):
        self._popup.dismiss()

    def update_cut_songs_list_view(self):
        """
        Updates the ListView with the current cut songs list.
        """
        app = App.get_running_app()
        self.cut_songs_property = app.cut_songs()

    def load(self, path, filename):
        app = App.get_running_app()
        cut_songs = app.cut_songs()
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
    theme_cls = ThemeManager()

    def build(self):
        # json_store_path = App.get_running_app().json_store_path
        json_store_path = self.json_store_path
        self.store = JsonStore(json_store_path)
        return Controller()

    @property
    def json_store_path(self):
        """
        Returns the JSON store file path.
        """
        return os.path.join(self.user_data_dir, JSON_STORE_PATH)

    def cut_songs(self):
        """
        Returns the current interruption songs list (full path).
        """
        try:
            songs = self.store.get('cut_songs')['list']
        except KeyError:
            songs = []
        return songs

    def timer_min(self):
        """
        Returns the current timer min value.
        """
        try:
            timer = self.store.get('timer_min')['list']
        except KeyError:
            timer = 0
        return timer

    def timer_max(self):
        """
        Returns the current timer max value.
        """
        try:
            timer = self.store.get('timer_max')['list']
        except KeyError:
            timer = 0
        return timer

if __name__ == '__main__':
    ControllerApp().run()
