import os
from os.path import expanduser
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivymd.theming import ThemeManager
from kivymd.navigationdrawer import NavigationDrawer
from kivymd.list import IRightBodyTouch, OneLineRightIconListItem
from kivymd.selectioncontrols import MDCheckbox
from jukebar import JukebarThread


JSON_STORE_PATH = "config.json"


class MainScreen(Screen):
    toggle_juke_property = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.jukebar_thread = None

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
        # self.jukebar_thread.join()

    def before_start_checks(self):
        """
        Verifies some cut songs are available before starting.
        Returns True if checks went OK.
        """
        app = App.get_running_app()
        if len(app.cut_songs()) == 0:
            popup = PopupMessage(
                    title="Error",
                    body="Your interruption songs list is empty.")
            popup.open()
            return False
        return True

    def toggle_juke_action(self, button):
        action_start = button.text == "Start Juke"
        if action_start:
            if not self.before_start_checks():
                return
            self.start_juke_action()
            button.text = "Stop Juke"
        else:
            self.stop_juke_action()
            button.text = "Start Juke"

class AboutScreen(Screen):
    about_text_property = StringProperty("" +
    """
    Project source code and info available on GitHub at:
    [color=00BFFF][ref=github]https://github.com/jeremyklelifa/Jukebar[/ref][/color]
    """)


class PopupMessage(Popup):
    title = StringProperty()
    body = StringProperty()


class LoadDialog(FloatLayout):
    path = StringProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MDCheckboxRight(IRightBodyTouch, MDCheckbox):
    pass


class SettingScreen(Screen):
    timer_max_property = ObjectProperty()
    timer_min_property = ObjectProperty()
    cut_songs_mdl_property = ObjectProperty()

    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)
        # for some reason cut_songs_mdl_property is None
        # if calling straight away
        Clock.schedule_once(
            lambda dt: self.update_widgets(), 0)

    def on_pre_leave(self):
        """
        Saves settings.
        """
        app = App.get_running_app()
        app.store.put('timer_min', value=self.timer_min_property.value)
        app.store.put('timer_max', value=self.timer_max_property.value)

    def show_load(self):
        app = App.get_running_app()
        path = app.sound_path()
        content = LoadDialog(
            load=self.load, cancel=self.dismiss_popup, path=path)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def delete_music(self):
        cut_songs_mdl_property = self.cut_songs_mdl_property
        app = App.get_running_app()
        cut_songs = app.cut_songs()
        for item in cut_songs_mdl_property.children:
            checkbox = item.children[0].children[0]
            if checkbox.state == "down":
                cut_songs.remove(item.text)
        app.store.put('cut_songs', list=cut_songs)
        self.update_cut_songs_list_view()

    def dismiss_popup(self):
        self._popup.dismiss()

    def update_min_max_sliders(self):
        """
        Updates the min and max timer sliders last saved state.
        """
        app = App.get_running_app()
        self.timer_min_property.value = app.timer_min()
        self.timer_max_property.value = app.timer_max()

    def update_cut_songs_list_view(self):
        """
        Updates the ListView with the current cut songs list.
        """
        cut_songs_mdl_property = self.cut_songs_mdl_property
        app = App.get_running_app()
        cut_songs = app.cut_songs()
        cut_songs_mdl_property.clear_widgets()
        for cut_song in cut_songs:
            item = OneLineRightIconListItem(text=cut_song)
            # checkbox = MDCheckbox()
            checkbox = MDCheckboxRight()
            item.add_widget(checkbox)
            cut_songs_mdl_property.add_widget(item)

    def update_widgets(self):
        """
        Updates widgets with previous saved state.
        """
        self.update_cut_songs_list_view()
        self.update_min_max_sliders()

    def load(self, path, filename):
        app = App.get_running_app()
        # updates the last used sound path
        app.store.put('sound_path', value=path)
        cut_songs = app.cut_songs()
        cut_songs.extend(filename)
        app.store.put('cut_songs', list=cut_songs)
        self.update_cut_songs_list_view()
        self.dismiss_popup()


class Controller(FloatLayout):
    '''Create a controller that receives a custom widget from the kv lang file.

    Add an action to be called from the kv lang file.
    '''
    pass


class JukebarNavigationDrawer(NavigationDrawer):
    pass


class ControllerApp(App):
    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()

    def build(self):
        # json_store_path = App.get_running_app().json_store_path
        json_store_path = self.json_store_path
        self.store = JsonStore(json_store_path)
        self.nav_drawer = JukebarNavigationDrawer()
        return Controller()

    def on_start(self):
        """
        Binds keyboard keys.
        """
	EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        """
        Binds the escape key with screen manager actions.
        Escapes the application if the current screen is "main"
        otherwise goes back to the main screen.
        """
        escape_key = 27
	if key == escape_key:
	   # do what you want, return True for stopping the propagation
           screen_manager = self.root.ids['screen_manager']
           if screen_manager.current != 'main':
               screen_manager.current = 'main'
               return True

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
            timer = self.store.get('timer_min')['value']
        except KeyError:
            timer = 0
        return timer

    def timer_max(self):
        """
        Returns the current timer max value.
        """
        try:
            timer = self.store.get('timer_max')['value']
        except KeyError:
            timer = 10
        return timer

    def sound_path(self):
        """
        Returns the most relevant sound path location:
        Returns the last used one or default to the home directory.
        """
        try:
            path = self.store.get('sound_path')['value']
        except KeyError:
            path = expanduser("~")
        return path


if __name__ == '__main__':
    ControllerApp().run()
