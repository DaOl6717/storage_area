def manual_input_menu(): #TODO
    user_chose = choice("Choose an option:'\n'[1] Add product'\n'[2] Remove product'\n' [3] Exit'\n'")
    
    if (user_chose == 1):
        add_product()
    elif (user_chose == 2):
        remove_product()
    elif (user_chose == 3):
        exit_program()  
    pass
