import json
import time
import threading
import paho.mqtt.client as mqtt

from credentials import MQTT_HOST, MQTT_USER, MQTT_PASS

# MQTT Client Setup
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(MQTT_HOST, 1883, 60)

threading.Thread(target=client.loop_forever, daemon=True).start()

response_cache = {}

def mqtt_request_response(request_topic, response_topic, payload, timeout=2):
    response_cache[response_topic] = None

    def on_message(client, userdata, msg):
        response_cache[msg.topic] = json.loads(msg.payload.decode())

    client.subscribe(response_topic)
    client.on_message = on_message

    client.publish(request_topic, json.dumps(payload))

    start = time.time()
    while time.time() - start < timeout:
        if response_cache[response_topic] is not None:
            return response_cache[response_topic]
        time.sleep(0.05)

    return None

# Helper function
def mqtt_publish(topic, payload_dict):
    client.publish(topic, json.dumps(payload_dict))

def barcode_exists(barcode):
    response = mqtt_request_response(
        request_topic="storage_room/request/barcode_exists",
        response_topic="storage_room/response/barcode_exists",
        payload={"barcode": barcode}
    )

    if response is None:
        return False  # if HA does not respond

    return response.get("exists", False)


def find_id_at_location(location):
    response = mqtt_request_response(
        request_topic="storage_room/request/find_location",
        response_topic="storage_room/response/find_location",
        payload={"location": location}
    )

    if response is None:
        return None

    return response.get("location_id")


def create_product(barcode, name, brand):
    mqtt_publish("storage_room/update", {
        "action": "create_product",
        "barcode": barcode,
        "name": name,
        "brand": brand
    })


def get_quantity(barcode):
    response = mqtt_request_response(
        request_topic="storage_room/request/get_quantity",
        response_topic="storage_room/response/get_quantity",
        payload={"barcode": barcode}
    )

    if response is None:
        return 0

    return response.get("quantity", 0)


def calculated_quantity(barcode, input_quant=None):
    if input_quant is None:
        return get_quantity(barcode)
    return input_quant


def add_inventory(quantity, expiry_date, barcode, name, brand, location_data):
    mqtt_publish("storage_room/update", {
        "action": "add_inventory",
        "barcode": barcode,
        "name": name,
        "brand": brand,
        "quantity": quantity,
        "expiry": str(expiry_date),
        "location": location_data
    })


def remove_from_product(barcode, rem_quantity):
    mqtt_publish("storage_room/update", {
        "action": "remove_inventory",
        "barcode": barcode,
        "quantity": rem_quantity
    })

    return "SENT"