from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.list import (
    MDListItem,
)

from kivy.properties import (
    ObjectProperty,
    StringProperty,
)

import pwd_manager_utils
import uuid


class ItemBind(MDListItem):
    app_name = StringProperty(None)
    app_user = StringProperty(None)
    app_pwd = StringProperty(None)
    app_info = StringProperty(None)

    def selected_item(self):
        from pwd_manager_kivy import ListScreen

        ListScreen().selected(self.app_name)


class AddEntryCard(MDCard):
    def __init__(self, **kwargs):
        super(AddEntryCard, self).__init__(**kwargs)

    def reset_card(self, **kwargs):
        self.clear_widgets()

    id = ""
    button_text = StringProperty("ADD ENTRY")
    title_text = "ADD AN ENTRY"

    app_name_input = ObjectProperty(None)
    app_user_input = ObjectProperty(None)
    app_pwd_input = ObjectProperty(None)
    app_pwd_confirm = ObjectProperty(None)
    app_info_text = ObjectProperty(None)

    app_name_update = ObjectProperty("")
    app_user_update = ObjectProperty("")
    app_pwd_update = ObjectProperty("")
    app_info_update = ObjectProperty("")

    def new_entry_details(self):
        error = False
        app_name_text = self.app_name_input.text.strip()
        app_user_text = self.app_user_input.text.strip()
        app_pwd_text = self.app_pwd_input.text
        app_pwd_confirm_text = self.app_pwd_confirm.text
        app_info_text = self.app_info.text

        if app_name_text == "":
            pwd_manager_utils.show_message(
                "ERROR", "The name of the app cannot be empty"
            )
            error = True

        elif app_user_text == "":
            pwd_manager_utils.show_message(
                "ERROR", "The username/e-mail of the app cannot be empty"
            )
            error = True

        elif not pwd_manager_utils.check_input(app_user_text):
            pwd_manager_utils.show_message(
                "ERROR", "Invalid characters in the username/e-mail"
            )
            error = True

        elif len(app_pwd_text) >= 8:
            if not pwd_manager_utils.check_input(app_pwd_text):
                pwd_manager_utils.show_message(
                    "ERROR", "Invalid characters in the password"
                )
                error = True
            elif app_pwd_text != app_pwd_confirm_text:
                pwd_manager_utils.show_message("ERROR", "Passwords don't match")
                error = True
        else:
            pwd_manager_utils.show_message(
                "ERROR",
                "Password must be at least 8 characters",
            )
            error = True

        if not error:
            self.parent.remove_widget(self)
            self.add_entry(
                uuid.uuid4().hex,
                app_name_text,
                app_user_text,
                app_pwd_text,
                app_info_text,
                "app_icon",
            )

    def add_entry(self, id, app_name, app_user, app_pwd, app_info, app_icon):
        from pwd_manager_listscreen import SearchBar

        app = MDApp.get_running_app()
        listscreen = app.root.current_screen
        master_list = SearchBar().master_list

        if pwd_manager_utils.app_name_exists(app_name, self.button_text, listscreen):
            return

        if self.button_text == "UPDATE":
            pwd_manager_utils.update_json(
                listscreen,
                id,
                app_name,
                app_user,
                app_pwd,
                app_info,
                app_icon,
            )

            master_list.pop(listscreen.selected_item)
            master_list[app_name] = [
                app_user,
                app_pwd,
                app_info,
                app_icon,
                id,
            ]

        else:
            pwd_manager_utils.add_to_json(
                id, app_name, app_user, app_pwd, app_info, app_icon
            )
            master_list[app_name] = [
                app_user,
                app_pwd,
                app_info,
                app_icon,
                id,
            ]
            SearchBar().refresh_lists(master_list)

        entries_list = listscreen.ids.entries_list

        if self.button_text == "UPDATE":
            for child in entries_list.children:
                if child.app_name == listscreen.selected_item:
                    entry_index = entries_list.children.index(child)
                    break
            entries_list.remove_widget(entries_list.children[entry_index])

        listscreen.bottom_bar_change(False)
        listscreen.reset_selected()

        pwd_manager_utils.add_entry_list(
            entries_list, id, app_name, app_user, app_pwd, app_info, app_icon
        )

        entries_list.children = sorted(
            entries_list.children,
            key=lambda x: x.app_name.casefold(),
            reverse=True,
        )
