from kivy_garden.frostedglass import FrostedGlass

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldMaxLengthText,
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.appbar import MDActionBottomAppBarButton
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.card import MDCard

# from kivymd.uix.list import (
#     TwoLineIconListItem,
#     IconLeftWidget,
#     ImageLeftWidgetWithoutTouch,
# )
# from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    ObjectProperty,
    StringProperty,
    ListProperty,
    BooleanProperty,
)

import os
import pwd_manager_utils
from pwd_manager_addentrycard import AddEntryCard


class BottomAppBarButton(MDActionBottomAppBarButton):
    theme_icon_color = "Custom"
    icon_color = "#8A8D79"


class SearchBar(MDTextField):
    theme_bg_color = "Custom"
    fill_color_normal = "#FFFFFF"

    available_apps = ListProperty()
    av_apps_1 = ListProperty()
    av_apps_2 = ListProperty()
    av_apps_3 = ListProperty()
    av_apps_4 = ListProperty()
    av_apps_ids = ListProperty()

    def __init__(self, **kwargs):
        super(SearchBar, self).__init__(**kwargs)
        user_data = pwd_manager_utils.load_user_json()
        self.available_apps = [
            pwd_manager_utils.decrypt_data(bytes(item[2:-1], "utf-8")).casefold()
            for item in user_data
        ]
        self.av_apps_ids = [user_data[item][4] for item in user_data]
        self.av_apps_1 = [app[0].casefold() for app in self.available_apps]
        self.av_apps_2 = [app[:2].casefold() for app in self.available_apps]
        self.av_apps_3 = [app[:3].casefold() for app in self.available_apps]
        self.av_apps_4 = [app[:4].casefold() for app in self.available_apps]
        self.av_apps = {
            1: self.av_apps_1,
            2: self.av_apps_2,
            3: self.av_apps_3,
            4: self.av_apps_4,
        }

    def on_focus(self, instance, input_text):
        super(SearchBar, self).on_focus(instance, input_text)

    def get_whole_list(self):
        app = MDApp.get_running_app()
        listscreen = app.root.current_screen
        entries_list = listscreen.ids.entries_list
        user_data = pwd_manager_utils.load_user_json()

        for item in user_data:
            id = user_data[item][4]
            app_name = pwd_manager_utils.decrypt_data(bytes(item[2:-1], "utf-8"))
            app_user = pwd_manager_utils.decrypt_data(
                bytes(user_data[item][0][2:-1], "utf-8")
            )
            app_pwd = pwd_manager_utils.decrypt_data(
                bytes(user_data[item][1][2:-1], "utf-8")
            )
            app_info = pwd_manager_utils.decrypt_data(
                bytes(user_data[item][2][2:-1], "utf-8")
            )
            app_icon = user_data[item][3]

            pwd_manager_utils.add_entry_list(
                entries_list,
                id,
                app_name,
                app_user,
                app_pwd,
                app_info,
                app_icon,
            )

        entries_list.children = sorted(
            entries_list.children,
            key=lambda x: x.app_name.casefold(),
            reverse=True,
        )

    def on_text(self, instance, input_text):
        print("ON TEXT")
        user_data = pwd_manager_utils.load_user_json()

        app = MDApp.get_running_app()
        listscreen = app.root.current_screen
        entries_list = listscreen.ids.entries_list

        if input_text == "":
            entries_list.clear_widgets()
            self.get_whole_list()
            # entries_list.disabled = True
            # entries_list.opacity = 0
            # entries_list.disabled = False
            # entries_list.opacity = 1

        elif len(input_text) < 5:
            entries_list.clear_widgets()
            current_list = self.av_apps[len(input_text)]
            if input_text in current_list:
                for h in range(len(current_list)):
                    app = current_list[h]
                    if app.startswith(input_text):
                        for item in user_data:
                            if user_data[item][4] == self.av_apps_ids[h]:
                                id = user_data[item][4]
                                app_name = pwd_manager_utils.decrypt_data(
                                    bytes(item[2:-1], "utf-8")
                                )
                                if not app_name.casefold().startswith(input_text):
                                    continue
                                app_user = pwd_manager_utils.decrypt_data(
                                    bytes(user_data[item][0][2:-1], "utf-8")
                                )
                                app_pwd = pwd_manager_utils.decrypt_data(
                                    bytes(user_data[item][1][2:-1], "utf-8")
                                )
                                app_info = pwd_manager_utils.decrypt_data(
                                    bytes(user_data[item][2][2:-1], "utf-8")
                                )
                                app_icon = user_data[item][3]

                                pwd_manager_utils.add_entry_list(
                                    entries_list,
                                    id,
                                    app_name,
                                    app_user,
                                    app_pwd,
                                    app_info,
                                    app_icon,
                                )

                            entries_list.children = sorted(
                                entries_list.children,
                                key=lambda x: x.app_name.casefold(),
                                reverse=True,
                            )


class ListScreen(MDScreen):
    selected_item = ""
    top_bar_text = StringProperty("")
    bottom_bar_text = StringProperty("")
    new_entry = None

    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        # self.new_entry = None

    def bottom_bar_change(self, status):
        if status:
            for child in self.ids.entries_list.children:
                if child.app_name == self.selected_item:
                    current_item = child
                    break

            self.ids.bottom_appbar.action_items = [
                BottomAppBarButton(
                    icon="open-in-new",
                    icon_color=MDApp.get_running_app().theme_cls.listscreenTopAppBarIconColor,
                    on_release=lambda x: (
                        pwd_manager_utils.show_message(
                            self.selected_item,
                            f"• username/e-mail:\n»»» {current_item.app_user}\n• password:\n»»» {current_item.app_pwd}\n• info:\n»»» {current_item.app_info}",
                        )
                    ),
                ),
                BottomAppBarButton(
                    icon="pencil",
                    icon_color=MDApp.get_running_app().theme_cls.listscreenTopAppBarIconColor,
                    on_release=lambda x: self.update_card(),
                ),
            ]
            self.ids.fab_button.icon = "trash-can"
            # self.ids.fab_button.md_bg_color = "#373A22"
            self.ids.fab_button.icon_color = (
                MDApp.get_running_app().theme_cls.listscreenBottomAppBarTrashIconSelected
            )
            self.ids.fab_button.md_bg_color = (
                MDApp.get_running_app().theme_cls.listscreenBottomAppBarTrashIconBgSelected
            )

            if len(self.selected_item) > 15:
                self.bottom_bar_text = f"{self.selected_item[:15]}..."
            else:
                self.bottom_bar_text = self.selected_item

        else:
            self.ids.bottom_appbar.action_items = ["", ""]
            self.ids.fab_button.icon = "trash-can-outline"
            self.ids.fab_button.icon_color = (
                MDApp.get_running_app().theme_cls.listscreenBottomAppBarTrashIcon
            )
            self.ids.fab_button.md_bg_color = (
                MDApp.get_running_app().theme_cls.listscreenBottomAppBarTrashIconBg
            )

            self.bottom_bar_text = ""

    def selected(self, app_name, *args):
        self.selected_item = app_name
        self.bottom_bar_change(True)

    def on_pre_enter(self):
        # def on_enter(self):
        dico = {
            "Amazon": "amazon_pwd",
            "Netflix": "netflix_pwd",
            "Gmail": "gmail_pwd",
        }

        icons = ["pencil", "android", "power"]

        user_data = pwd_manager_utils.load_user_json()
        for item in user_data:
            id = user_data[item][4]
            app_name = pwd_manager_utils.decrypt_data(bytes(item[2:-1], "utf-8"))
            app_user = pwd_manager_utils.decrypt_data(
                bytes(user_data[item][0][2:-1], "utf-8")
            )
            app_pwd = pwd_manager_utils.decrypt_data(
                bytes(user_data[item][1][2:-1], "utf-8")
            )
            app_info = pwd_manager_utils.decrypt_data(
                bytes(user_data[item][2][2:-1], "utf-8")
            )
            app_icon = user_data[item][3]

            pwd_manager_utils.add_entry_list(
                self.ids.entries_list,
                id,
                app_name,
                app_user,
                app_pwd,
                app_info,
                app_icon,
            )

        self.ids.entries_list.children = sorted(
            self.ids.entries_list.children,
            key=lambda x: x.app_name.casefold(),
            reverse=True,
        )

    def on_enter(self):
        self.top_bar_text = os.environ.get("pwdzmanuser")

    def reset_selected(self):
        if self.selected_item != "":
            self.selected_item = ""
            self.bottom_bar_change(False)

    def add_card(self):
        self.new_entry = AddEntryCard(md_bg_color=(1, 1, 1, 0.9))
        self.add_widget(self.new_entry)

    def update_card(self):
        for child in self.ids.entries_list.children:
            if child.app_name == self.selected_item:
                current_item = child

        self.new_entry = AddEntryCard(
            button_text="UPDATE",
            md_bg_color=(1, 1, 1, 0.9),
        )
        self.new_entry.app_name_update = current_item.app_name
        self.new_entry.app_user_update = current_item.app_user
        self.new_entry.app_pwd_update = current_item.app_pwd
        self.new_entry.app_info_update = current_item.app_info
        self.add_widget(self.new_entry)

    def remove_card(self):
        self.reset_selected()
        self.remove_widget(self.new_entry)
        self.new_entry = None

    def remove_entry(self):
        for child in self.ids.entries_list.children:
            if child.app_name == self.selected_item:
                entry_index = self.ids.entries_list.children.index(child)
                current_item = child
                break
        self.ids.entries_list.remove_widget(self.ids.entries_list.children[entry_index])
        pwd_manager_utils.remove_entry_json(self.selected_item, current_item)
        self.reset_selected()

    def logout(self):
        os.environ["pwdzmanuser"] = ""
        self.selected_item = ""
        self.ids.entries_list.clear_widgets()
        self.manager.current = "loginscreen"
        self.manager.get_screen("listscreen").clear_widgets()
        self.manager.remove_widget(self.manager.get_screen("listscreen"))
        # app.screenmanager.remove_widget(app.screenmanager.get_screen("listscreen")
