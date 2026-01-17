import mysql.connector
import paho.mqtt.publish as publish
import json
from datetime import datetime
from credentials import ip_address, db_username, db_password, db_name
from user_defined_variables import using_barcode_scanner, scan_alt_0, scan_alt_1, scan_alt_2

global program_running
program_running = False

# Database connection, config in credentials.py
db = mysql.connector.connect(
    host=ip_address,
    user=db_username,
    password=db_password,
    database=db_name
)

cursor = db.cursor()

def barcode_exists(barcode):
    cursor.execute("select barcode from product where barcode = %s", (barcode,))
    result = cursor.fetchone()
    
    return result is not None

def find_id_at_location(location):

    section = location[0]
    floor = int(location[1])
    F_or_B = location[2]
    
    cursor.execute("select id from location where section = %s and floor = %s and F_or_B = %s", (section, floor, F_or_B))
    result = cursor.fetchone()
    
    if result:
        return result[0] # type: ignore
    
    cursor.execute("insert into location (floor, section, F_or_B) values (%s, %s, %s)", (floor, section, F_or_B))
        
    return cursor.lastrowid

def create_product(barcode, name, brand):
    cursor.execute("insert into product (barcode, name, brand) values (%s, %s, %s)", (barcode, name, brand))
    db.commit()

def get_quantity(barcode):
    cursor.execute("select quantity from inventory where product_id = %s", (barcode,)) # type: ignore
    return cursor.fetchone()[0] # type: ignore

def calculated_quantity(barcode, input_quant=None):
    # If user does no specify a new quantity
    if input_quant is None:
        new_quantity = get_quantity(barcode)
    # Overwrite old quantity
    else:
        new_quantity = input_quant

    return new_quantity

def add_inventory(quantity, expiry_date, barcode, name, brand, location_data):
    if not barcode_exists(barcode):
        create_product(barcode, name, brand)

    location_id = find_id_at_location(location_data)
    
    # Check if product already at this specific location
    query = "SELECT id, quantity FROM inventory WHERE product_id = %s AND location_id = %s"
    cursor.execute(query, (barcode, location_id))
    result = cursor.fetchone()

    if result:
        inventory_id = result[0]
        new_total = result[1] + quantity
        update_query = "UPDATE inventory SET quantity = %s, last_updated = %s WHERE id = %s"
        cursor.execute(update_query, (new_total, datetime.now(), inventory_id))
    else:
        insert_query = """INSERT INTO inventory (quantity, expiry_date, last_updated, location_id, product_id) 
                          VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(insert_query, (quantity, expiry_date, datetime.now(), location_id, barcode))
    
    db.commit()

def remove_from_product(barcode, rem_quantity):
    if (barcode_exists(barcode) == True):
        current_quantity = get_quantity(barcode) # type: ignore
        
        if (current_quantity < 1 or current_quantity < rem_quantity): # type: ignore
            return "NO INVENTORY"
        
        cursor.execute("update inventory set quantity = %s where product_id = %s", (current_quantity - rem_quantity, barcode)) # type: ignore
        return "UPDATED"
    else:
        return "DOES NOT EXIST"