import time
import hid
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "localhost"  # Change to your MQTT broker IP or hostname (e.g., 192.168.1.50)
MQTT_PORT = 1883
MQTT_TOPIC = "retro/phone/button"
MQTT_CLIENT_ID = "PythonRetroPhone"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected successfully to MQTT Broker!")
    else:
        print(f"Failed to connect to MQTT broker, return code {rc}")

def setup_mqtt_client():
    """Initializes and connects the MQTT client."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        return client
    except Exception as e:
        print(f"MQTT Connection Error: {e}")
        return None

def get_phone_device():
    """Finds and opens the retro phone HID device."""
    devices = hid.enumerate()
    target = None

    for d in devices:
        prod_name = (d.get('product_string') or "").lower()
        if any(keyword in prod_name for keyword in ["phone", "audio", "handset", "telephony", "retro"]):
            target = d
            break
    
    if not target and devices:
        target = devices[0]

    if target:
        print(f"Connected to: {target.get('product_string', 'Unknown Device')} (VID: {hex(target['vendor_id'])}, PID: {hex(target['product_id'])})")
        device = hid.device()
        device.open_path(target['path'])
        return device
    return None

def parse_button_event(data):
    if not data or len(data) < 2:
        return None
    
    report_id = data[0]
    key_code = data[1]

    if report_id == 3:
        if key_code == 1:
            return "volume_up"
        elif key_code == 2:
            return "volume_down"
        elif key_code == 4:
            return "call_toggle"
    return None

def main():
    # Setup MQTT
    mqtt_client = setup_mqtt_client()
    if not mqtt_client:
        print("Running without MQTT publishing (broker unreachable).")

    device = get_phone_device()
    if not device:
        print("Error: No suitable USB HID device found.")
        if mqtt_client:
            mqtt_client.loop_stop()
        return

    device.set_nonblocking(True)
    print(f"Publishing phone button events to topic: '{MQTT_TOPIC}'...\n")

    last_pressed_button = None

    try:
        while True:
            data = device.read(64)
            if data:
                key_code = data[1] if len(data) > 1 else 0

                if key_code != 0:
                    button_event = parse_button_event(data)
                    if button_event and button_event != last_pressed_button:
                        print(f"Button Action Detected: {button_event}")
                        if mqtt_client:
                            mqtt_client.publish(MQTT_TOPIC, button_event)
                        last_pressed_button = button_event
                else:
                    last_pressed_button = None

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nStopping MQTT phone script...")
    finally:
        device.close()
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        print("Cleaned up and shut down.")

if __name__ == "__main__":
    main()
