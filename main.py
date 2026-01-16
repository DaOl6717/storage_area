from user_defined_variables import using_barcode_scanner
from db_ops_barcode_only import scanner_menu
from db_ops_text_inut import manual_input_menu

def main():   
    print("Script started.")
    
    if (using_barcode_scanner):
        scanner_menu()
    else:
        manual_input_menu()