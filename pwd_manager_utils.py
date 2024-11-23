import hashlib
import plyer
from datetime import datetime
import json
import os
from os.path import exists
import platform
import configparser
import bcrypt
import base64
import gc
from configparser import ConfigParser
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from kivymd.app import MDApp
from kivymd.uix.list import (
    MDListItemHeadlineText,
    MDListItemTrailingIcon,
)

from kivy.uix.button import Button
from kivy.uix.popup import Popup

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from pwd_manager_addentrycard import ItemBind


FILENAME = "config.ini"


def process_message(message):
    message = message.replace("\n", " [returnz] ")
    desired_length = 44
    height = 1
    if len(message) > desired_length:
        message = message.split(" ")
        sentence = ""
        long_message = ""
        for u in range(len(message)):
            word = message[u]
            word = word.strip()
            if word == "[returnz]":
                word = ""
            else:
                if len(sentence + word) <= desired_length:
                    sentence += f"{word} "
                    if u == len(message):
                        height += 1
                        break
                    continue
            long_message += f"{sentence.strip()}\n"
            height += 1
            sentence = f"{word} "
        long_message += f"{sentence.strip()}"
        message = long_message
    return message, height


def show_message(title, message):
    message, height = process_message(message)
    backup = False

    if "[backup]" in title:
        title = title.replace("[backup]", "")
        backup = True

    btn_ok = Button(
        text="OK" if not backup else "CONFIRM BACK UP",
        background_color=MDApp.get_running_app().theme_cls.popupButtonBg,
        background_normal="",
        size_hint=(0.4, None) if not backup else (0.6, None),
        height="40dp",
        pos_hint={"center_x": 0.5},
    )

    btn_close = Button(
        text="CANCEL",
        background_color=MDApp.get_running_app().theme_cls.popupButtonBg,
        background_normal="",
        size_hint=(0.4, None) if not backup else (0.6, None),
        height="40dp",
        pos_hint={"center_x": 0.5},
    )

    # layout = MDBoxLayout(orientation="vertical")
    layout = MDBoxLayout(
        MDLabel(
            text=message,
            text_color="FFFFFF",
            adaptive_size=True,
            padding=("5dp", 0, 0, 0),
            # pos=("12dp", "12dp"),
        ),
        orientation="vertical",
        theme_bg_color="Custom",
        md_bg_color=(0, 0, 0, 0),
        radius=0,
        spacing="10dp",
    )

    update_btns_layout = MDBoxLayout(
        orientation="horizontal",
        theme_bg_color="Custom",
        md_bg_color=(0, 0, 0, 0),
        radius=0,
        spacing="10dp",
    )

    if backup:
        update_btns_layout.add_widget(btn_ok)
        update_btns_layout.add_widget(btn_close)
        layout.add_widget(update_btns_layout)

    else:
        layout.add_widget(btn_ok)

    popup = Popup(
        title=title,
        title_size="20sp",
        content=layout,
        background="",
        background_color=MDApp.get_running_app().theme_cls.popupBg,
        overlay_color=MDApp.get_running_app().theme_cls.popupBgOverlay,
        size_hint=(None, None),
        size=("350dp", f"{(120) + 23*height}dp"),
    )

    popup.open()

    # btn_ok.bind(on_release=popup.dismiss)
    if backup:
        username = os.environ.get("pwdzmanuser")
        btn_ok.bind(on_release=lambda x: backup_data(username))

    btn_ok.bind(on_release=popup.dismiss)
    btn_close.bind(on_release=popup.dismiss)


def hasher(word, salt):
    sha256 = hashlib.sha256()
    sha256.update((word + salt).encode())
    return sha256.hexdigest()


def generate_salt():
    return bcrypt.gensalt()


def check_input(word):
    if " " not in word or word == "":
        if word.isascii():
            return word
    return False


def initialize_config_file(filename=FILENAME):
    parser = ConfigParser()
    parser.read(filename)
    try:
        parser.add_section("theme")
        parser.set("theme", "theme-colors", "blue-purple")

        with open(filename, "w") as configfile:
            parser.write(configfile)
    except configparser.DuplicateSectionError:
        pass


def load_theme(filename=FILENAME):
    parser = ConfigParser()
    parser.read(filename)
    params = parser.items("theme")
    theme = params[0][1]
    return theme


def update_theme(theme, filename=FILENAME):
    parser = ConfigParser()
    parser.read(filename)
    parser.set("theme", "theme-colors", theme)
    with open(filename, "w") as configfile:
        parser.write(configfile)


def add_user(
    username,
    password,
    salt,
    device_id,
    filename=FILENAME,
):
    """Update the config INI file after having filled in
    the fields. Note that the config file will be automatically
    created if it doesn't exist"""

    parser = ConfigParser()
    parser.read(filename)
    try:
        parser.add_section(username)
    except configparser.DuplicateSectionError:
        print("Section already exists, skipping that step.")
        return "user_exists"

    parser.set(username, "password", password)
    parser.set(username, "salt", salt)
    parser.set(username, "device id", device_id)

    with open(filename, "w") as configfile:
        parser.write(configfile)


def app_name_exists(app_name, button_text, listscreen):
    username = hasher(os.environ.get("pwdzmanuser"), "")
    with open(f"{username}.json", "r") as file:
        user_data = json.load(file)
        apps_names = [decrypt_data(bytes(item[2:-1], "utf-8")) for item in user_data]
        print("apps_names:", apps_names)
        if app_name in apps_names and button_text != "UPDATE":
            show_message(
                "ERROR",
                f"{app_name} has already been added. Please update it by selecting it in your list and then clicking the little pencil.",
            )
            return True
        elif button_text == "UPDATE":
            if app_name in apps_names and app_name != listscreen.selected_item:
                show_message(
                    "ERROR",
                    f"{app_name} is already in use, please choose another name.",
                )
                return True

        return False


def add_to_json(id, app_name, app_user, app_pwd, app_info, app_icon):
    username = hasher(os.environ.get("pwdzmanuser"), "")

    if not exists(f"{username}.json"):
        print("JSON doesn't exist, creating it...")
        with open(f"{username}.json", "w") as file:
            json.dump(
                {
                    str(encrypt_data(app_name)): [
                        str(encrypt_data(app_user)),
                        str(encrypt_data(app_pwd)),
                        str(encrypt_data(app_info)),
                        app_icon,
                        id,
                    ]
                },
                file,
                indent=4,
            )

    else:
        with open(f"{username}.json", "r") as file:
            user_data = json.load(file)
            user_data.update(
                {
                    str(encrypt_data(app_name)): [
                        str(encrypt_data(app_user)),
                        str(encrypt_data(app_pwd)),
                        str(encrypt_data(app_info)),
                        app_icon,
                        id,
                    ]
                }
            )
        with open(f"{username}.json", "w") as file:
            json.dump(user_data, file, indent=4)


def load_user_json():
    try:
        username = hasher(os.environ.get("pwdzmanuser"), "")

        if not exists(f"{username}.json"):
            print("JSON doesn't exist, creating it...")
            with open(f"{username}.json", "w") as file:
                json.dump({}, file)

        with open(f"{username}.json", "r") as file:
            user_data = json.load(file)
            return user_data
    except:
        print("Error in loading user")
    # except:
    #     return []


def update_json(listscreen, id, app_name, app_user, app_pwd, app_info, app_icon):
    username = hasher(os.environ.get("pwdzmanuser"), "")
    selected_item = listscreen.selected_item
    entries_list = listscreen.ids.entries_list

    # if app_name_exists(username, app_name):
    #     return True

    for child in entries_list.children:
        if child.app_name == selected_item:
            current_item = child
            break

    with open(f"{username}.json", "r") as file:
        user_data = json.load(file)

        for item in user_data:
            if user_data[item][4] == current_item.id:
                user_data.pop(item)
                break

        user_data.update(
            {
                str(encrypt_data(app_name)): [
                    str(encrypt_data(app_user)),
                    str(encrypt_data(app_pwd)),
                    str(encrypt_data(app_info)),
                    app_icon,
                    id,
                ]
            }
        )

    with open(f"{username}.json", "w") as file:
        json.dump(user_data, file, indent=4)


def remove_entry_json(selected_item, current_item):
    username = hasher(os.environ.get("pwdzmanuser"), "")
    with open(f"{username}.json", "r") as file:
        user_data = json.load(file)
        for item in user_data:
            if user_data[item][4] == current_item.id:
                user_data.pop(item)
                break
        # user_data.pop(selected_item)
        with open(f"{username}.json", "w") as file:
            json.dump(user_data, file, indent=4)


def add_entry_list(entries_list, id, app_name, app_user, app_pwd, app_info, app_icon):
    entries_list.add_widget(
        ItemBind(
            MDListItemHeadlineText(
                text=app_name,
                theme_text_color="Custom",
                text_color=MDApp.get_running_app().theme_cls.listscreenTextColor,
            ),
            # MDListItemSupportingText(
            #     text=app_pwd,
            # ),
            MDListItemTrailingIcon(
                icon=app_icon, theme_icon_color="Custom", icon_color="FFFFFF"
            ),
            id=id,
            app_name=app_name,
            app_user=app_user,
            app_pwd=app_pwd,
            app_info=app_info,
        ),
    )


def check_login_pwd(user, filename=FILENAME):
    parser = ConfigParser()
    parser.read(filename)
    params = parser.items(hasher(user, ""))
    password = params[0][1]
    salt = params[1][1]
    return password, salt


def load_config_info(filename=FILENAME):
    parser = ConfigParser()
    parser.read(filename)
    # for item in parser.items():
    #     if item[0] == "autologin":
    #         print("AUTOLOGIN FOUND")
    params = parser.items(hasher("user_test", ""))
    print("Config file loaded")


def list_users(username, password, filename=FILENAME):
    parser = ConfigParser()
    parser.read(filename)
    # for item in parser.items():
    return [item[0] for item in parser.items()]


def auto_login(filename=FILENAME):
    autologin = False
    parser = ConfigParser()
    parser.read(filename)
    for item in parser.items():
        if item[0] == "autologin":
            autologin = True
            break
    return autologin


def get_sys_info():
    system_info = platform.uname()

    print("System Information:")
    print(f"System: {system_info.system}")
    print(f"Node Name: {system_info.node}")
    print(f"Release: {system_info.release}")
    print(f"Version: {system_info.version}")
    print(f"Machine: {system_info.machine}")
    print(f"Processor: {system_info.processor.replace(' ', '')}")

    device_id = plyer.uniqueid.id
    print(f"Device unique ID: {device_id}")


def make_key():
    sha256 = hashlib.sha256()
    user = os.environ.get("pwdzmanuser")
    password, salt = check_login_pwd(user, filename=FILENAME)
    # password = bytes(password, "utf-8")
    # device_id = hasher(plyer.uniqueid.id, salt)
    device_id = plyer.uniqueid.id
    # derivation = bytes(salt + device_id, "utf-8")
    sha256.update((device_id + password + salt).encode())
    key = base64.b64encode(sha256.digest())

    # kdf = PBKDF2HMAC(
    #     algorithm=hashes.SHA256(),
    #     length=32,
    #     salt=derivation,
    #     iterations=480000,
    # )
    # key = base64.b64encode(kdf.derive(password))
    key = base64.b64encode(sha256.digest())
    return key


def encrypt_data(data):
    key = make_key()
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(bytes(data, "utf-8"))
    del key
    gc.collect()
    return encrypted_message


def decrypt_data(data):
    key = make_key()
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(data).decode()
    del key
    gc.collect()
    return decrypted_message


def back_data_prompt(username):
    show_message(
        "BACK UP DATA?[backup]",
        """You are about to back your data up.\n\nBeware! The exported data will NOT be encrypted, so anyone who has access to it will have access to your passwords! \nDon't lose it and keep it safe!""",
    )


def backup_data(username):
    user_hashed = hasher(username, "")
    filename = f'{username}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    backup_file = open(filename, "w")

    with open(f"{user_hashed}.json", "r") as file:
        user_data = json.load(file)
        for item in user_data:
            app_name = decrypt_data(bytes(item[2:-1], "utf-8"))
            app_user = decrypt_data(bytes(user_data[item][0][2:-1], "utf-8"))
            app_pwd = decrypt_data(bytes(user_data[item][1][2:-1], "utf-8"))
            app_info = decrypt_data(bytes(user_data[item][2][2:-1], "utf-8"))

            if app_info != "":
                app_info = f"info: {app_info}"
            backup_file.write(
                f"[{app_name}]\nuser/e-mail: {app_user}\npassword: {app_pwd}\n{app_info}\n"
            )

    show_message(
        "DATA BACKED UP",
        f"""Your data was successfully backed up!\nYou will find it in the file "{filename}".\n\nAnd remember! The data in that file is NOT encrypted!""",
    )
