import time
import hid

# Configuration: If you know your retro phone's Vendor ID (VID) and Product ID (PID),
# fill them in here. Leave them as None to auto-detect or list connected devices.
VENDOR_ID = None   # Example: 0x1234
PRODUCT_ID = None  # Example: 0x5678

def list_connected_hid_devices():
    """Lists all connected HID devices to help find the retro phone's VID/PID."""
    print("Scanning for connected USB HID devices...")
    for device_info in hid.enumerate():
        print(
            f"Device: {device_info['product_string']} "
            f"(VID: {hex(device_info['vendor_id'])} | "
            f"PID: {hex(device_info['product_id'])})"
        )

def listen_to_phone():
    """Connects to the USB retro phone and listens for button presses."""
    device = None
    
    try:
        if VENDOR_ID and PRODUCT_ID:
            print(f"Connecting to device VID: {hex(VENDOR_ID)}, PID: {hex(PRODUCT_ID)}...")
            device = hid.device()
            device.open(VENDOR_ID, PRODUCT_ID)
        else:
            print("No VID/PID specified. Trying to find a potential USB phone device...")
            devices = hid.enumerate()
            
            # Simple heuristic: look for common keywords in product strings or pick the first available
            target = None
            for d in devices:
                prod_name = (d.get('product_string') or "").lower()
                if any(keyword in prod_name for keyword in ["phone", "audio", "handset", "telephony", "retro"]):
                    target = d
                    break
            
            if not target and devices:
                # Fallback to the first interactive device if none match keywords
                target = devices[0]
                
            if target:
                print(f"Opening device: {target['product_string']} (VID: {hex(target['vendor_id'])}, PID: {hex(target['product_id'])})")
                device = hid.device()
                device.open_path(target['path'])
            else:
                print("Error: No USB HID devices found.")
                return

        # Set device to non-blocking mode (optional, or use blocking reads)
        device.set_nonblocking(True)
        print("Successfully connected! Press phone buttons (Volume Up, Down, Call). Press Ctrl+C to exit.\n")

        while True:
            # Read raw data packets from the device (adjust buffer size if necessary, e.g., 64 bytes)
            data = device.read(64)
            if data:
                print(f"Raw data received: {data}")
                
                # Note: Exact byte mapping depends on your specific hardware model.
                # Typically, consumer control devices send specific report layouts.
                # You can map the incoming bytes here once you inspect the output of each key.
                
            time.sleep(0.05)

    except IOError as e:
        print(f"Hardware communication error: {e}")
    except KeyboardInterrupt:
        print("\nStopping listener script...")
    finally:
        if device:
            device.close()
            print("Device connection closed safely.")

if __name__ == "__main__":
    # Uncomment the line below if you need to look up your device's Vendor/Product IDs first
    # list_connected_hid_devices()
    
    listen_to_phone()
