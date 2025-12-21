from user_defined_variables import using_barcode_scanner
from database_operations_barcode import scanner_menu
from database_operations_user_input import manual_input_menu

def main():   
    print("Script started.")
    
    if (using_barcode_scanner):
        scanner_menu()
    else:
        manual_input_menu()