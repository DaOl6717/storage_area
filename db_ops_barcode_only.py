import mysql.connector
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

def choice(prompt):
    user_input = input(prompt)
    return user_input

def get_barcode():
    barcode = input("Scan the barcode: ")
    return barcode

def barcode_exists(barcode):
    cursor.execute("select barcode from product where barcode = %s", (barcode,))
    result = cursor.fetchone()
    return result is not None

def specify_location():
    selected_place = get_barcode()
    selected_section = get_barcode()
    
    cursor.execute("select id from location where place = %s and section = %s", (selected_place, selected_section))
    result = cursor.fetchone()
    
    if result:
        return result[0] # type: ignore
    
    cursor.execute("insert into location (place, section) values (%s, %s)", (selected_place, selected_section))
        
    return cursor.lastrowid

def create_product(barcode, product_name):
    cursor.execute("insert into product (barcode, name) values (%s, %s, %s)", (barcode, product_name,))
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

def modify_inventory():
    barcode = get_barcode()
    new_product = False
    
    # If product does not exist
    if (barcode_exists(barcode) == False):
        product_name = f"New product {barcode} added: {datetime.now}"
        create_product(barcode, product_name)
        new_product = True
    
    location_id = specify_location()
 
    # Create or update the inventory
    if (new_product):
        cursor.execute("insert into inventory (quantity, product_id, location_id) values (%s, %s, %s)", (1, barcode, location_id)) # type: ignore
    else:
        new_quantity = calculated_quantity(barcode)
        cursor.execute("insert into inventory (quantity, product_id, location_id) values (%s, %s, %s)", (new_quantity, barcode, location_id)) # type: ignore
    
    db.commit()

def remove_product(barcode):
    if (barcode_exists(barcode) == True):
        current_quantity = get_quantity(barcode) # type: ignore
        
        if (current_quantity < 1): # type: ignore
            return
        
        cursor.execute("update inventory set quantity = %s where product_id = %s", (current_quantity - 1, barcode)) # type: ignore
    else:
        print("Product does not exist.")

def scanner_menu():
    print("Note: The prints in this mode are only for debugging.")
    program_running = True
    
    while (program_running):
        print(f"Choose between 'Add to your inventory'={scan_alt_0}, 'Remove a product'={scan_alt_1}, 'Exit'={scan_alt_2}")
        user_input = choice("Make a choice.")
        
        if (user_input == scan_alt_0):
            modify_inventory()
        elif (user_input == scan_alt_1):
            product_to_remove = get_barcode()
            remove_product(product_to_remove)
        elif (user_input == scan_alt_2):
            exit_program()

def exit_program():
    print("Exiting program")
    program_running = False


def main():
    cursor = db.cursor()
    
    print("Script started, scanner mode.")
    scanner_menu()