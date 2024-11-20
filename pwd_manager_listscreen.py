from kivy_garden.frostedglass import FrostedGlass

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
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
from kivymd.uix.list import (
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingIcon,
)

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
        # key = pwd_manager_utils.make_key()
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
