# version v1.0.4

import ctypes
import subprocess
import os
import json
import time
import ctypes
import platform
import win32gui
import win32con
from win10toast import ToastNotifier
import tkinter as tk
from tkinter import ttk
from threading import Thread

# Hide the console window
if os.name == 'nt':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Define the path for the settings file
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), 'settings.txt')

# Initialize the settings file
def init_settings_file():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "filePath": "C:\\Program Files\\Hubstaff",
            "hubstaffShortcutPath": "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Hubstaff\\Hubstaff.lnk",
            "delay": 4,
            "popUpNotification": 1,
            "popUpHubStaff": 0,
            "screenLock": 0
        }
        save_settings_to_file(default_settings)

# Function to save settings to a text file
def save_settings_to_file(settings):
    with open(SETTINGS_FILE, 'w') as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")
    print("Settings saved to file.")

# Function to read settings from a text file
def read_settings_from_file():
    if not os.path.exists(SETTINGS_FILE):
        init_settings_file()
    
    settings = {}
    with open(SETTINGS_FILE, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            settings[key] = int(value) if value.isdigit() else value
    return settings

# Function to show Windows notification
def pushWindowsNotification(title, message):
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=0)  # Duration is in seconds

# Function to bring Hubstaff window to the foreground
def popUpHubstaff(hubstaffShortcutPath):
    try:
        if platform.system() == "Windows":
            os.startfile(hubstaffShortcutPath)
            time.sleep(5)  # Wait for the application to fully open
            app_window = win32gui.FindWindow(None, "Hubstaff")
            if app_window:
                win32gui.ShowWindow(app_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(app_window)
            else:
                print("Hubstaff window not found.")
        else:
            print("Currently, only Windows is supported for direct shortcut opening.")
    except Exception as e:
        print(f"Failed to start or bring Hubstaff to foreground: {e}")

# Function to check Hubstaff tracking status
def HubstaffTracking(filePath):
    os.chdir(filePath)
    result = subprocess.run(['HubstaffCLI', 'status'], shell=True, capture_output=True, text=True)
    mixed_text = result.stdout
    json_start_index = mixed_text.find('{')
    json_end_index = mixed_text.rfind('}') + 1
    json_str = mixed_text[json_start_index:json_end_index]

    try:
        data = json.loads(json_str)
        tracking_value = data.get('tracking')
        print("Tracking:", tracking_value == True)
        return tracking_value == True
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in output")

# Main tracking loop
def tracking_loop():
    false_count = 0
    start_time = time.time()

    while True:
        settings = read_settings_from_file()
        filePath = settings.get('filePath', '')
        screenLock = settings.get('screenLock', 0)
        popUpNotification = settings.get('popUpNotification', 0)
        popUpHubStaff = settings.get('popUpHubStaff', 0)
        delay = settings.get('delay', 0)
        hubstaffShortcutPath = settings.get('hubstaffShortcutPath', '')

        result = HubstaffTracking(filePath)
        if result:
            false_count = 0
        else:
            false_count += 1
            if false_count * 1 > delay:
                elapsed_time = time.time() - start_time
                print(f"Alert! Hubstaff tracking is off")

                if popUpNotification == 1:
                    pushWindowsNotification('Hubstaff Tracking Off', "Your hubstaff tracking is turned off")

                if popUpHubStaff == 1:
                    popUpHubstaff(hubstaffShortcutPath)

                if screenLock == 1:
                    ctypes.windll.user32.LockWorkStation()

                false_count = 0
        time.sleep(1)

# Function to save settings to text file
def save_settings():
    settings = {
        "filePath": file_path_entry.get(),
        "hubstaffShortcutPath": shortcut_path_entry.get(),
        "delay": int(delay_entry.get()) if delay_unit.get() == "Seconds" else int(delay_entry.get()) * 60,
        "popUpNotification": 1 if popup_notification_var.get() == "On" else 0,
        "popUpHubStaff": 1 if popup_hubstaff_var.get() == "On" else 0,
        "screenLock": 1 if screen_lock_var.get() == "On" else 0
    }
    save_settings_to_file(settings)

# Function to create GUI
def create_gui():
    root = tk.Tk()
    root.title("Hubstaff Tracker Settings")

    settings = read_settings_from_file()

    # File path
    tk.Label(root, text="File Path:").grid(row=0, column=0, padx=10, pady=5)
    global file_path_entry
    file_path_entry = tk.Entry(root, width=50)
    file_path_entry.grid(row=0, column=1, padx=10, pady=5)
    file_path_entry.insert(0, settings.get("filePath", ""))

    # Hubstaff shortcut path
    tk.Label(root, text="Hubstaff Shortcut Path:").grid(row=1, column=0, padx=10, pady=5)
    global shortcut_path_entry
    shortcut_path_entry = tk.Entry(root, width=50)
    shortcut_path_entry.grid(row=1, column=1, padx=10, pady=5)
    shortcut_path_entry.insert(0, settings.get("hubstaffShortcutPath", ""))

    # Delay
    tk.Label(root, text="Delay:").grid(row=2, column=0, padx=10, pady=5)
    global delay_entry
    delay_entry = tk.Entry(root, width=10)
    delay_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    delay_entry.insert(0, settings.get("delay", ""))
    global delay_unit
    delay_unit = ttk.Combobox(root, values=["Seconds", "Minutes"], width=10)
    delay_unit.grid(row=2, column=1, padx=10, pady=5, sticky="e")
    delay_unit.current(0 if settings.get("delay", 0) < 60 else 1)

    # Popup notification
    tk.Label(root, text="Popup Notification:").grid(row=3, column=0, padx=10, pady=5)
    global popup_notification_var
    popup_notification_var = tk.StringVar(value="On" if settings.get("popUpNotification", 1) == 1 else "Off")
    popup_notification_dropdown = ttk.Combobox(root, textvariable=popup_notification_var, values=["On", "Off"], width=10)
    popup_notification_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    # Popup Hubstaff
    tk.Label(root, text="Popup Hubstaff:").grid(row=4, column=0, padx=10, pady=5)
    global popup_hubstaff_var
    popup_hubstaff_var = tk.StringVar(value="On" if settings.get("popUpHubStaff", 0) == 1 else "Off")
    popup_hubstaff_dropdown = ttk.Combobox(root, textvariable=popup_hubstaff_var, values=["On", "Off"], width=10)
    popup_hubstaff_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    # Screen lock
    tk.Label(root, text="Screen Lock:").grid(row=5, column=0, padx=10, pady=5)
    global screen_lock_var
    screen_lock_var = tk.StringVar(value="On" if settings.get("screenLock", 0) == 1 else "Off")
    screen_lock_dropdown = ttk.Combobox(root, textvariable=screen_lock_var, values=["On", "Off"], width=10)
    screen_lock_dropdown.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    # Save button
    save_button = tk.Button(root, text="Save Settings", command=save_settings)
    save_button.grid(row=6, columnspan=2, pady=20)

    # Start the tracking loop in a separate thread
    tracking_thread = Thread(target=tracking_loop)
    tracking_thread.daemon = True
    tracking_thread.start()

    root.mainloop()

if __name__ == "__main__":
    init_settings_file()
    create_gui()
