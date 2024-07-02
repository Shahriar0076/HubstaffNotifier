import subprocess
import os
import json
import time
import ctypes
import json
import platform
import win32gui
import win32con
from win10toast import ToastNotifier

def show_message_box(message, title):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1)

def push_windows_notification(title, message):
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=0)  # Duration is in seconds

def HubstaffTracking(filePath):
    # Change directory to C:\Program Files\Hubstaff
    os.chdir(filePath)

    # Run HubstaffCLI and capture the output
    result = subprocess.run(['HubstaffCLI', 'status'], shell=True, capture_output=True, text=True)

    # Store the output in a variable
    mixed_text = result.stdout
    
    # Find the start and end of the JSON part
    json_start_index = mixed_text.find('{')
    json_end_index = mixed_text.rfind('}') + 1  # rfind to find the last occurrence, +1 to include the '}'

    # Extract the JSON part
    json_str = mixed_text[json_start_index:json_end_index]

    # Parse the JSON string
    try:
        data = json.loads(json_str)
        tracking_value = data.get('tracking')
        print("Tracking value:", tracking_value == True)
        return tracking_value == True
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in output")  

def run_hubstaff(hubstaffShortcutPath):
    try:
        if platform.system() == "Windows":
            # Start Hubstaff
            os.startfile(hubstaffShortcutPath)
            # Wait for the application to fully open (adjust time as needed)
            time.sleep(5)
            # Find the window handle and bring it to the foreground
            app_window = win32gui.FindWindow(None, "Hubstaff")  # Adjust window title if necessary
            if app_window:
                win32gui.ShowWindow(app_window, win32con.SW_RESTORE)  # Restore the window if minimized                
                win32gui.SetForegroundWindow(app_window)  # Bring the window to the foreground                
            else:
                print("Hubstaff window not found.")
        else:
            print("Currently, only Windows is supported for direct shortcut opening.")
    except Exception as e:
        push_windows_notification('Hubstaff Tracking Off', "Your hubstaff tracking is turned off")
        print(f"Failed to start or bring Hubstaff to foreground: {e}")  

def main():
    with open('settings.json', 'r') as file:
        data = json.load(file)

    filePath             = data.get('filePath', '')
    screenLock           = data.get('screenLock', '')    
    popUpWindow          = data.get('popUpWindow', '')    
    popUpNotification    = data.get('popUpNotification', '')    
    delay                = data.get('delay', '')    
    hubstaffShortcutPath = data.get('hubstaffShortcutPath', '')    

    false_count = 0
    alert_threshold = delay  # 5 minutes in seconds
    # alert_threshold = 5 * 60  # 5 minutes in seconds
    start_time = time.time()
    
    while True:
        result = HubstaffTracking(filePath)       
        
        if result:
            false_count = 0
        else:
            false_count += 1
            
            # Check if more than 5 minutes have passed
            if false_count * 1 > alert_threshold:
                elapsed_time = time.time() - start_time
                print(f"Alert! Hubstaff tracking is off)")

                if popUpNotification == 1:
                    push_windows_notification('Hubstaff Tracking Off', "Your hubstaff tracking is turned off")

                if popUpWindow == 1:
                    run_hubstaff(hubstaffShortcutPath)

                if screenLock == 1:
                    ctypes.windll.user32.LockWorkStation()

                # show_message_box("Hubstaff client is not active. Please start the application.", "Hubstaff Alert")

                false_count = 0  # Reset false count after alert
        
        time.sleep(1)  # Adjust the sleep interval as needed

if __name__ == "__main__":
    main()