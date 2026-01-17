import json
import time
import threading
import paho.mqtt.client as mqtt
from credentials import MQTT_HOST, MQTT_USER, MQTT_PASS

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(MQTT_HOST, 1883, 60)

response_cache = {}

def on_message(client, userdata, msg):
    try:
        response_cache[msg.topic] = json.loads(msg.payload.decode())
    except:
        response_cache[msg.topic] = msg.payload.decode()

client.on_message = on_message
threading.Thread(target=client.loop_forever, daemon=True).start()

def mqtt_request_response(request_topic, response_topic, payload, timeout=2):
    response_cache[response_topic] = None
    client.subscribe(response_topic)
    client.publish(request_topic, json.dumps(payload))

    start = time.time()
    while time.time() - start < timeout:
        if response_cache.get(response_topic) is not None:
            return response_cache[response_topic]
        time.sleep(0.05)
    return None

def barcode_exists(barcode):
    response = mqtt_request_response(
        request_topic="storage_room/request/barcode_exists",
        response_topic="storage_room/response/barcode_exists",
        payload={"barcode": barcode}
    )
    return response.get("exists", False) if response else False

def find_id_at_location(location_barcode):
    response = mqtt_request_response(
        request_topic="storage_room/request/find_location",
        response_topic="storage_room/response/find_location",
        payload={"location": location_barcode}
    )
    # Returns the location_id if it exists, else None
    return response.get("location_id") if response else None

def add_inventory(quantity, expiry_date, barcode, name, brand, location_data):
    # This now uses a request-response to confirm the DB actually saved it
    response = mqtt_request_response(
        request_topic="storage_room/update",
        response_topic="storage_room/response/add_status",
        payload={
            "action": "add_inventory",
            "barcode": barcode,
            "name": name,
            "brand": brand,
            "quantity": quantity,
            "expiry": str(expiry_date),
            "location": location_data
        }
    )
    return response.get("success", False) if response else False