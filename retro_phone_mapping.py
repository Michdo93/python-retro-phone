import time
import hid

# Configuration: Optional Vendor ID / Product ID filter. 
# Leave as None to automatically detect the first available telephony/audio USB device.
VENDOR_ID = None
PRODUCT_ID = None

def get_phone_device():
    """Finds and opens the retro phone HID device."""
    devices = hid.enumerate()
    target = None

    if VENDOR_ID and PRODUCT_ID:
        for d in devices:
            if d['vendor_id'] == VENDOR_ID and d['product_id'] == PRODUCT_ID:
                target = d
                break
    else:
        # Heuristic search for communication or audio handsets
        for d in devices:
            prod_name = (d.get('product_string') or "").lower()
            if any(keyword in prod_name for keyword in ["phone", "audio", "handset", "telephony", "retro"]):
                target = d
                break
        
        # Fallback to the first available HID device if no keyword matched
        if not target and devices:
            target = devices[0]

    if target:
        print(f"Connected to: {target.get('product_string', 'Unknown Device')} (VID: {hex(target['vendor_id'])}, PID: {hex(target['product_id'])})")
        device = hid.device()
        device.open_path(target['path'])
        return device
    
    return None

def parse_button_event(data):
    """
    Parses the raw HID byte array based on observed hardware protocol:
    - data[1] == 1 -> Volume Up
    - data[1] == 2 -> Volume Down
    - data[1] == 4 -> Call / End Call
    - data[1] == 0 -> Key Released
    """
    if not data or len(data) < 2:
        return None
    
    report_id = data[0]
    key_code = data[1]

    if report_id == 3:
        if key_code == 1:
            return "Volume Up"
        elif key_code == 2:
            return "Volume Down"
        elif key_code == 4:
            return "Call / End Call"
            
    return None

def main():
    device = get_phone_device()
    if not device:
        print("Error: No suitable USB HID device found. Make sure your retro phone is plugged in.")
        return

    device.set_nonblocking(True)
    print("Listening for button presses... Press Ctrl+C to exit.\n")

    last_pressed_button = None

    try:
        while True:
            data = device.read(64)
            if data:
                # Check key state code at index 1
                key_code = data[1] if len(data) > 1 else 0

                if key_code != 0:
                    # Button press event detected
                    button_name = parse_button_event(data)
                    if button_name and button_name != last_pressed_button:
                        print(f"Button Pressed: {button_name}")
                        last_pressed_button = button_name
                else:
                    # Button release event (key_code == 0)
                    last_pressed_button = None

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nStopping button mapper script...")
    finally:
        device.close()
        print("Device connection closed.")

if __name__ == "__main__":
    main()
