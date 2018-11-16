from kivymd.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from kivymd.theming import ThemeManager

class AcceptButton(MDRaisedButton):
    def on_disabled(self, instance, value):
        #self._update_color()
        print("instance.disabled is", instance.disabled)
        if instance.disabled:
            self._current_button_color = self.md_bg_color_disabled
            print(self._current_button_color)
        else:
            self._current_button_color = self.md_bg_color

class AcceptButton2(Button):
    pass

class Page(BoxLayout):
    
    def accept_mission(self):
        accept_button = self.ids.accept_button
        accept_button.disabled = True 
        #accept_button._update_color()
        print("md_bg_color_disabled is:", accept_button.md_bg_color_disabled)
        print(accept_button._current_button_color)
        color = accept_button.canvas.children[1]
        print("Color is:", color.r, color.g, color.b, color.a)
        self.mission.start()
        print("mission started")
        accept_button._update_color()

class ButtonTest2App(App):
    theme_cls = ThemeManager()
    def Build(self):
        parent = Page()
        return parent

if __name__ == "__main__":
    ButtonTest2App().run()