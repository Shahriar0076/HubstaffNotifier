# version 1.0.1

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
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1)
    except:
        print("There was an in show_message_box")
    

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
    json_end_index = mixed_text.rfind('}') + 1

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

def main():
    with open('settings.json', 'r') as file:
        data = json.load(file)

    filePath             = data.get('filePath', '')
    screenLock           = data.get('screenLock', '')    
    popUpWindow          = data.get('popUpWindow', '')    
    popUpNotification    = data.get('popUpNotification', '')    
    delay                = data.get('delay', '')

    false_count = 0
    alert_threshold = delay
    start_time = time.time()
    
    while True:
        result = HubstaffTracking(filePath)       
        
        if result:
            false_count = 0
        else:
            false_count += 1
            
            # Check if more than alert_threshold minutes have passed
            if false_count * 1 > alert_threshold:
                elapsed_time = time.time() - start_time
                print(f"Alert! Hubstaff tracking is off)")

                if popUpNotification == 1:
                    push_windows_notification('Hubstaff Tracking Off', "Your hubstaff tracking is turned off")                

                if screenLock == 1:
                    ctypes.windll.user32.LockWorkStation()                

                false_count = 0  # Reset false count after alert
        
        time.sleep(1)  # Adjust the sleep interval as needed

if __name__ == "__main__":
    main()