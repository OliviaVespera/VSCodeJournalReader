from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior

from kivy.graphics import Bezier
from kivy.properties import StringProperty, OptionProperty, ListProperty, BooleanProperty
from kivy.config import Config
from kivymd.ripplebehavior import CircularRippleBehavior
from kivymd.button import MDIconButton, MDFlatButton, MDRaisedButton
from kivymd.navigationdrawer import NavigationLayout, NavigationDrawerIconButton, MDNavigationDrawer
from kivymd.theming import ThemeManager

from win32api import GetCursorPos

from mission_manager.app import Application
from mission_manager.mission import Dock, Tour, Mission
from mission_manager.mission_enums import MissionStatus

from uuid import uuid4
import json
class AcceptButton(MDRaisedButton):
    """def on_disabled(self, instance, value):
        #self._update_color()
        print("instance.disabled is", instance.disabled)
        if instance.disabled:
            self._current_button_color = self.md_bg_color_disabled
            print(self._current_button_color)
        else:
            self._current_button_color = self.md_bg_color"""
    def on_release(self):
        self.parent.parent.accept_mission()
class MissionOption(NavigationDrawerIconButton):
    def __init__(self, **kwargs):
        self.text = kwargs.pop("text")
        self.mission_uid = kwargs.pop("uid")
        super().__init__(**kwargs)

class MissionNavigation(NavigationLayout):

    def load_missions(self):
        main_not_set = True
        for mission in App.get_running_app().core.missions():
            new_mission = MissionOption(
                text=mission.title, uid = mission.uid.int)
            if main_not_set:
                self.mission_details.update_mission_details(mission.uid.int)
                main_not_set = False
            self.ids.nav_drawer.add_widget(new_mission)
class MainLayout(BoxLayout):
    pass
class MissionDetails(BoxLayout):
    title = StringProperty()
    description = StringProperty()
    steps = StringProperty()
    image_source = StringProperty()
    current_task = StringProperty()
    mission = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_height(self):
        total_height = 0
        for element in self.ids:
           total_height +=  self.ids[element].height
        return total_height
    
    def update_mission_details(self, uid):
        self.mission = App.get_running_app().core.mission.get_by_uid(uid)
        self.description = self.mission.desc.get("body")
        self.image_source = self.mission.desc.get("image")
        self.title = self.mission.title
        print("title changed to {}".format(self.title))
        print("image changed to {}".format(self.image_source))
        if self.mission.status == MissionStatus.Not_Started:
            self.accept_button.disabled = False
            self.accept_button._update_color()
        else:
            self.accept_button.disabled = True
            self.accept_button._update_color()
        #steps = mission.step

    def accept_mission(self):
        self.accept_button.disabled = True
        self.mission.start()
        print("mission started")
        self.accept_button._update_color()
        

class MissionText(Label):
    pass

class ImageButton(CircularRippleBehavior, ButtonBehavior, BoxLayout):
	source = StringProperty('')
	theme_text_color = OptionProperty(None, allownone=True,
	                                  options=['Primary', 'Secondary', 'Hint',
	                                           'Error', 'Custom'])
	text_color = ListProperty(None, allownone=True)
	opposite_colors = BooleanProperty(False)

class StatusBar(Widget):
    pass
class WindowLayout(FloatLayout):
    pass

class WindowMover(Label):

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            print("\ttouch.pos =", touch.pos)
            self.touch_x, self.touch_y = touch.pos
            return True
        return super(WindowMover, self).on_touch_down(touch)

    def on_touch_move(self, touch):

        if self.collide_point(*touch.pos) and self.touch_x is not None:

            print("\ttouch.pos =", touch.pos)
            self.new_x, self.new_y = GetCursorPos()
            #Window.top +=  full_diff
            Window.top += (self.new_y - Window.top)-(Window.size[1]-self.touch_y)
            Window.left += (self.new_x - Window.left)-self.touch_x
            return True
        return super(WindowMover, self).on_touch_move(touch)

class MissionManagerGUIApp(App):
    theme_cls = ThemeManager()

    title = "Olivia's Mission Manager"    
    mission_text = StringProperty()
    core = Application()
    save_file = "mission_file.json"

    def build(self):
        
        self.load_mission_file()
        self.core.start()
        self.core.gui_loop()
        Clock.schedule_interval(self.core.gui_loop, 1)

        parent = WindowLayout()
        Window.size = (800, 800)
        #Window.borderless = True
        #self.write_config(700, 700)

        self.mission_text = (
        "Her Mother is worried about her and has put out a contract for her capture, "
        "[color=#CC1111][b]ALIVE[/b][/color]. "
        "Head to 9 Aurigae and search for signs of her.")

        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.accent_palette = "DeepOrange"
        parent.main_layout.ids.nav_layout.load_missions()
        print(parent.main_layout.ids.nav_layout.mission_details)
        return parent
    
    def main_loop(self):
        self.core.gui_loop
        #update properties.
    
    def get_mission_info(self):
        for mission in self.core.mission.missions:
            pass

    def write_config(self, width, height):
        Config.set('graphics', 'resizable', True)
        Config.set('graphics', 'width', width)
        Config.set('graphics', 'height', height)
        Config.write()

    def load_mission_file(self):
        """mission = Mission()
        dock.save(save_file)
        tour.save(save_file)"""
        with open(self.save_file, mode="r", encoding="UTF-8") as m_file:
            buffer = [json.loads(line) for line in m_file]

        for line in buffer:
            mission = Mission.load(line)
            self.core.missions().append(mission)
        #self.core.mission.start_all()
    def on_stop(self):
        print("we're saving the mission")
        self.core.mission.save(self.save_file)

if __name__ == "__main__":
    MissionManagerGUIApp().run()