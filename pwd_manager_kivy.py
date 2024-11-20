from kivy_garden.frostedglass import FrostedGlass

from kivymd.app import MDApp

# from kivymd.tools.hotreload.app import MDApp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingIcon,
)
from kivymd.uix.textfield import MDTextField
from kivymd.uix.appbar import MDActionBottomAppBarButton

from kivy.event import EventDispatcher
from kivy.uix.scrollview import ScrollView
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager  # , Screen
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    ListProperty,
    BooleanProperty,
)
import json, os
from os.path import exists
import platform
import plyer
import pwd_manager_utils
from pwd_manager_listscreen import ListScreen

Window.size = 414, 736


def unload_file():
    from kivy.lang.builder import BuilderBase

    BuilderBase().unload_file("passmanager.kv")


class LoginScreen(MDScreen):
    username_input = ObjectProperty(None)
    password_input_login = ObjectProperty(None)
    username_input_reg = ObjectProperty(None)
    password_input_reg = ObjectProperty(None)
    password_input_confirm = ObjectProperty(None)

    device_id = plyer.uniqueid.id
    new_data = None
    file = None
    file_exists = None
    path = "log.json"
    config_filename = "config.ini"
    input_color = 0, 0.2, 0, 0.5
    btn_color = 0.2, 0, 0, 1
    white = 1, 1, 1, 0.5

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.username_input.text = "user_test"

    def on_leave(self, *args):
        self.username_input.text = ""
        self.password_input_login.text = ""
        self.username_input_reg.text = ""
        self.password_input_reg.text = ""
        self.password_input_confirm.text = ""

    def confirm_backup(self, confirmation):
        return confirmation

    def user_login(self, export):
        username_text = self.username_input.text
        current_user = pwd_manager_utils.hasher(username_text, "")
        password_text = self.password_input_login.text
        users = pwd_manager_utils.list_users(username_text, password_text)
        if current_user in users:
            print(f"{username_text} exists in DB")
            password, salt = pwd_manager_utils.check_login_pwd(username_text)
            # if pwd_manager_utils.hasher(password_text, salt) == password:
            os.environ["pwdzmanuser"] = username_text
            os.environ["pwdzmanpwd"] = password_text
            current_user_env = os.environ["pwdzmanuser"]
            # print(f"\n\t{current_user_env}'s password:", os.environ["pwdzmanpwd"])
            if export:
                pwd_manager_utils.back_data_prompt(username_text)
                # pwd_manager_utils.backup_data(username_text, current_user)
            else:
                # self.manager.add_widget(ListScreen(name="listscreen"))

                self.manager.current = "listscreen"
            # else:
            #     pwd_manager_utils.show_message(
            #         "ERROR", "username does not exist or wrong password"
            #     )
            #     self.username_input.text = ""
            #     self.password_input_login.text = ""

        else:
            pwd_manager_utils.show_message(
                "ERROR", "username does not exist or wrong password"
            )
            self.username_input.text = ""
            self.password_input_login.text = ""

    def new_user(self):
        user_data = True
        username_text = self.username_input_reg.text
        password_text = self.password_input_reg.text
        password_confirm_text = self.password_input_confirm.text

        if not pwd_manager_utils.check_input(username_text):
            pwd_manager_utils.show_message(
                "ERROR",
                "Invalid characters in the username 123490 Invalid characters\nin the username 123490 Invalid\ncharacters in \n the username 123490",
            )
            user_data = False
        else:
            if len(password_text) >= 8:
                if not pwd_manager_utils.check_input(password_text):
                    pwd_manager_utils.show_message(
                        "ERROR", "Invalid characters in the password"
                    )
                    user_data = False
                elif password_text != password_confirm_text:
                    pwd_manager_utils.show_message("ERROR", "Passwords don't match")
                    user_data = False
            else:
                pwd_manager_utils.show_message(
                    "ERROR",
                    "Password must be at least 8 characters",
                )
                user_data = False

        if user_data:
            salt = pwd_manager_utils.generate_salt().decode()
            #     pwd_manager_utils.load_config_info()  # debug

            if (
                pwd_manager_utils.add_user(
                    pwd_manager_utils.hasher(username_text, ""),
                    pwd_manager_utils.hasher(password_text, salt),
                    salt,
                    pwd_manager_utils.hasher(self.device_id, salt),
                    self.config_filename,
                )
                == "user_exists"
            ):
                pwd_manager_utils.show_message(
                    "ERROR", "That username is already used. Please chose another one."
                )
            pwd_manager_utils.show_message(
                "Banzai!",
                "You can now log in with the username and password you just registered \o/",
            )

        self.username_input_reg.text = ""
        self.password_input_reg.text = ""
        self.password_input_confirm.text = ""

    def set_theme(self, theme):
        app = MDApp.get_running_app()
        current_theme = pwd_manager_utils.load_theme()
        if theme != current_theme:
            pwd_manager_utils.update_theme(theme)
            app.screenmanager.remove_widget(app.screenmanager.get_screen("listscreen"))
            app.screenmanager.clear_widgets()
            Builder.unload_file("zupasswordz.kv")
            app.stop()
            return PassManagerApp().run()

    def app_information(self):
        pwd_manager_utils.show_message(
            "ZUPAsswordz Manager",
            """©munchou 2024

Tools of the trade: Python 3.10.2,
Kivy 2.3.0 and Kivy MD 2.0.1 (dev0).
And love. And time. And tears of blood...

The code is Open Source, feel free to study it, improve the app or reuse part of it. Do not hesitate to contact me for a collab'!
github.com/munchou/zupasswords-manager

Commercial use in any way is NOT allowed. Kindly contact before backstabbing, I'll put on my shiniest Leonardo's shell. Thanks.

Special thanks to Martin (OWDD), Snu and Cheaterman (both Kivy Discord)""",
        )


class PassManagerApp(MDApp):
    screenmanager = ScreenManager()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Builder.load_file("zupasswordz.kv")

    def build(self):
        pwd_manager_utils.initialize_config_file()
        # I am using 3 main colors + regular ones (like )background and white):
        # - background
        # - color1: top/bottom bars
        # - color2: textfields
        # - color3: buttons/list

        selected_theme = pwd_manager_utils.load_theme()

        if selected_theme == "blue-purple":
            background_color = "282e43"
            white = "FFFFFF"
            color1 = "5776ed"
            color2 = "b3c0f3"
            color3 = "8299f2"
        if selected_theme == "georgia-coffee":
            background_color = "200d09"
            white = "FFFFFF"
            color1 = "4e281d"
            color2 = "ad815e"
            color3 = "d2a821"
        if selected_theme == "macha":
            background_color = "0b2c1c"
            white = "FFFFFF"
            color1 = "1f5138"
            color2 = "9bb922"
            color3 = "53a12c"
        if selected_theme == "kirby":
            background_color = "4b2032"
            white = "FFFFFF"
            color1 = "98486a"
            color2 = "d6b2c4"
            color3 = "d285a5"
        if selected_theme == "suntory-coffee":
            background_color = "512d1c"
            white = "FFFFFF"
            color1 = "8d4f32"
            color2 = "b6956c"
            color3 = "b1714e"

        # General
        self.theme_cls.backgroundColor = background_color

        # Popup colors
        self.theme_cls.popupBg = background_color  # color1  #"4366ec"
        self.theme_cls.popupButtonBg = color3  # "1e3eb7"
        self.theme_cls.popupBgOverlay = (1, 1, 1, 0.4)
        # self.theme_cls.popupBgOverlay = (0.34, 0.463, 0.93, 0.6)

        # LoginScreen colors:
        self.theme_cls.textfieldBgColor = color2
        self.theme_cls.textfieldBgColorFocus = color1
        self.theme_cls.textfieldLineColor = color1
        self.theme_cls.textfieldLineColorFocus = color2

        self.theme_cls.textfieldTextColor = color1
        self.theme_cls.textfieldTextColorFocus = white

        self.theme_cls.textfieldHintTextColor = color1
        self.theme_cls.textfieldHintTextColorFocus = white

        self.theme_cls.textfieldIconColor = color2
        self.theme_cls.textfieldIconColorFocus = white

        self.theme_cls.buttonBackgroundColor = color3

        self.theme_cls.TopAppBarBgColor = color1
        self.theme_cls.TopAppBarTitleColor = white
        self.theme_cls.TopAppBarIconColor = color1
        self.theme_cls.TopAppBarIconBgColor = color2

        # ListScreen colors (many used in LoginScreen):
        self.theme_cls.listscreenTopAppBarBgColor = color1
        self.theme_cls.listscreenTopAppBarTitleColor = white
        self.theme_cls.listscreenTopAppBarIconColor = white
        self.theme_cls.listscreenTopAppBarIconBgColor = color2

        self.theme_cls.listscreenListBgColor = color3
        self.theme_cls.listscreenTextColor = white

        self.theme_cls.listscreenBottomAppBarBg = color1
        self.theme_cls.listscreenBottomAppBarTrashIcon = color1
        self.theme_cls.listscreenBottomAppBarTrashIconBg = color2
        self.theme_cls.listscreenBottomAppBarTrashIconSelected = white
        self.theme_cls.listscreenBottomAppBarTrashIconBgSelected = (
            background_color  # "3752bc"
        )

        # End of colors

        self.screenmanager.add_widget(LoginScreen(name="loginscreen"))
        self.screenmanager.add_widget(ListScreen(name="listscreen"))
        return self.screenmanager

    # def restart(self):
    #     self.screenmanager.clear_widgets()
    #     self.stop()
    #     return PassManagerApp().run()


if __name__ == "__main__":
    PassManagerApp().run()
