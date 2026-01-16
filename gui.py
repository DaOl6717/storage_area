import customtkinter as ctk
import db_ops_gui_and_barcode as db_ops

# ADD PRODUCT FLOW
# Barcode scan page TODO

# If barcode not in db:
    # Name input page TODO
    # Brand input page TODO

# Expiry date page TODO
# Quantity page TODO
# Location scan page TODO
# Confirm Add TODO
# Back to start page TODO

# REMOVE PRODUCT FLOW
# Barcode scan page TODO

# If barcode not in db:
    # Display error, go back to start screen TODO

# Quantity page TODO
    # If removing more than all stock, give error and display current stock
# Location scan page TODO
# Confirm Remove TODO
# Back to start page TODO


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Current Product (global)
        self.current_item = {
            "barcode": None,
            "name": None,
            "brand": None,
            "quantity": None,
            "location": None,
            "expiry": None
        }

        self.title("Pi Navigation System")
        #self.overrideredirect(True)
        self.attributes('-fullscreen', True)

        # Configure grid to fill the whole window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Dictionary to hold our "pages"
        self.frames = {}

        # Initialize all pages
        for PageClass in (MainMenu, AddPage, RemovePage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self, controller=self)
            self.frames[page_name] = frame
            # Stack all frames in the same grid cell
            frame.grid(row=0, column=0, sticky="nsew")

        # Start with the Main Menu
        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        """Bring a specific frame to the front"""
        frame = self.frames[page_name]
        frame.tkraise()

# Page 1: Main Menu
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Storage Management System", font=("Arial", 40)).pack(pady=30)

        # Navigation Buttons
        add_button = ctk.CTkButton(self, text="Add Product", font=("Arial", 40), width=325, height=80,
                             command=lambda: controller.show_frame("AddPage"), fg_color="#23d023")
        add_button.pack(side='left', anchor='e', expand=True, pady=10, padx=10)

        remove_button = ctk.CTkButton(self, text="Remove Product", font=("Arial", 40), width=60, height=80,
                             command=lambda: controller.show_frame("RemovePage"), fg_color='#f72a2a')
        remove_button.pack(side='right', anchor='w', expand=True, pady=10, padx=10)

# Page 2: Product Add page
class AddPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Add Product", font=("Arial", 40)).pack(pady=30)
        self.status_label = ctk.CTkLabel(self, text="Please Scan Product", font=("Arial", 30)).pack(pady=60)
        
        self.barcode_entry = ctk.CTkEntry(self, width=600, height=80, font=("Arial", 30), justify="center")
        self.barcode_entry.pack(pady=0)
        self.barcode_entry.bind('<Return>', self.process_scan)
        
        back_btn = ctk.CTkButton(self, text="Cancel", fg_color="#f72a2a", command=lambda: controller.show_frame("MainMenu"), width=120, height=60, font=("Arial", 30))
        back_btn.pack(pady=50)
        
        self.bind("<Visibility>", lambda e: self.barcode_entry.focus_set())
        
    def process_scan(self, event):
        barcode = self.barcode_entry.get().strip()
        self.controller.current_item["barcode"] = barcode
        
        if db_ops.barcode_exists(barcode):
            self.controller.show_frame("QuantityPage")
        else:
            self.controller.show_frame("NameInputPage")
        
        self.controller.current_item["barcode"] = barcode

class QuantityPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        return #TODO

class NameInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        return #TODO


# --- Page 3: Stats ---
class RemovePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="System Statistics", font=("Arial", 24))
        label.pack(pady=30)

        back_btn = ctk.CTkButton(self, text="Back to Home", fg_color="gray30",
                                 command=lambda: controller.show_frame("MainMenu"))
        back_btn.pack(side="bottom", pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()