import customtkinter as ctk
import db_operations_backend as db_ops

# ADD PRODUCT FLOW
# Barcode scan page

# If barcode not in db:
    # Name input page
    # Brand input page

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
        for PageClass in (MainMenu, AddPage, RemovePage, QuantityPage, NameInputPage, BrandInputPage):
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
        
# Custom on screen keyboard
class TouchKeyboard(ctk.CTkFrame):
    def __init__(self, parent, target_entry, enter_command):
        super().__init__(parent)
        self.target_entry = target_entry
        
        keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'Å'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ö', 'Ä'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '-']
        ]

        for row in keys:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(pady=2)
            for key in row:
                ctk.CTkButton(row_frame, text=key, width=70, height=70, font=("Arial", 32),
                              command=lambda k=key: self.target_entry.insert("insert", k)).pack(side="left", padx=2)

        # Controls
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(pady=10)

        ctk.CTkButton(ctrl_frame, text="«", width=120, height=70, fg_color="#d35400",
                      command=lambda: self.target_entry.delete(len(self.target_entry.get())-1, "end")).pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_frame, text="SPACE", width=300, height=70,
                      command=lambda: self.target_entry.insert("insert", " ")).pack(side="left", padx=5)

        ctk.CTkButton(ctrl_frame, text="»", width=120, height=70, fg_color="#23d023",
                      command=enter_command).pack(side="left", padx=5)

# Custom on screen numpad
class TouchNumpad(ctk.CTkFrame):
    def __init__(self, parent, target_entry, enter_command):
        super().__init__(parent)
        self.target_entry = target_entry
        
        keys = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['«', '0', '»']
        ]

        for row in keys:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(pady=2)
            for key in row:
                
                if key == "«":
                    ctk.CTkButton(row_frame, text="«", width=70, height=70, fg_color="#d35400",
                        command=lambda: self.target_entry.delete(len(self.target_entry.get())-1, "end")).pack(side="left", padx=5)
                    continue
                elif key == "»":
                    ctk.CTkButton(row_frame, text="»", width=70, height=70, fg_color="#23d023",
                        command=enter_command).pack(side="left", padx=5)
                    continue
                    
                ctk.CTkButton(row_frame, text=key, width=70, height=70, font=("Arial", 22),
                              command=lambda k=key: self.target_entry.insert("insert", k)).pack(side="left", padx=2)   

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
        
# Page 2.1: Prouct Name input
class NameInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Enter Product Name", font=("Arial", 40)).pack(pady=10)
        
        self.entry = ctk.CTkEntry(self, width=700, height=60, font=("Arial", 30), justify="center")
        self.entry.pack(pady=10)
        
        # Add keyboard - OK button calls self.next_step
        self.kb = TouchKeyboard(self, self.entry, self.next_step)
        self.kb.pack(pady=10)

    def next_step(self):
        self.controller.current_item["name"] = self.entry.get()
        self.entry.delete(0, 'end') # Clean up for next time
        self.controller.show_frame("BrandInputPage")

# Page 2.2: Prouct Brand input
class BrandInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Enter Brand", font=("Arial", 40)).pack(pady=10)
        
        self.entry = ctk.CTkEntry(self, width=700, height=60, font=("Arial", 30), justify="center")
        self.entry.pack(pady=10)
        
        self.kb = TouchKeyboard(self, self.entry, self.next_step)
        self.kb.pack(pady=10)

    def next_step(self):
        self.controller.current_item["brand"] = self.entry.get()
        self.entry.delete(0, 'end')
        self.controller.show_frame("QuantityPage")

# Page 2.3: Quantity Input
class QuantityPage(ctk.CTkFrame): #TODO
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Enter Quantity", font=("Arial", 40)).pack(pady=10)
        
        self.entry = ctk.CTkEntry(self, width=700, height=60, font=("Arial", 30), justify="center")
        self.entry.pack(pady=10)
        
        self.kb = TouchNumpad(self, self.entry, self.next_step)
        self.kb.pack(pady=10)

    def next_step(self):
        self.controller.current_item["quantity"] = int(self.entry.get())
        self.entry.delete(0, 'end')
        self.controller.show_frame("QuantityPage")

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