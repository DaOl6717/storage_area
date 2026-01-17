from datetime import datetime
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
        for PageClass in (MainMenu, AddPage, RemovePage, QuantityPage, NameInputPage, BrandInputPage, ExpiryInputPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self, controller=self)
            self.frames[page_name] = frame
            # Stack all frames in the same grid cell
            frame.grid(row=0, column=0, sticky="nsew")

        # Start with the Main Menu
        self.show_frame("MainMenu")

    def show_frame(self, page_name):
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

        ctk.CTkButton(ctrl_frame, text="«", width=120, height=70, font=("Arial", 40), fg_color="#d35400",
                      command=lambda: self.target_entry.delete(len(self.target_entry.get())-1, "end")).pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_frame, text="SPACE", width=300, height=70, font=("Arial", 32),
                      command=lambda: self.target_entry.insert("insert", " ")).pack(side="left", padx=5)

        ctk.CTkButton(ctrl_frame, text="»", width=120, font=("Arial", 40), height=70, fg_color="#23d023",
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
                    ctk.CTkButton(row_frame, text="«", width=70, height=70, font=("Arial", 40), fg_color="#d35400",
                        command=lambda: self.target_entry.delete(len(self.target_entry.get())-1, "end")).pack(side="left", padx=5)
                    continue
                elif key == "»":
                    ctk.CTkButton(row_frame, text="»", width=70, height=70, font=("Arial", 40), fg_color="#23d023",
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
            self.controller.show_frame("ExpiryInputPage")
        else:
            self.controller.show_frame("NameInputPage")
        
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
        self.controller.show_frame("ExpiryInputPage")

# Page 2.3: Expiry Date Input
class ExpiryInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Data lists
        self.years = [str(datetime.now().year + i) for i in range(11)]
        self.months = [f"{i:02d}" for i in range(1, 13)]
        self.days = [f"{i:02d}" for i in range(1, 32)]

        # Track current index for each column
        self.y_idx = 0
        self.m_idx = datetime.now().month - 1
        self.d_idx = 0

        ctk.CTkLabel(self, text="Select Expiry Date", font=("Arial", 40)).pack(pady=10)

        # Main Container
        self.columns_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.columns_frame.pack(expand=True, fill="both", padx=20)

        # Create the 3 Selectors
        self.year_label = self.create_selector("Year", self.years, self.y_idx, 0, "year")
        self.month_label = self.create_selector("Month", self.months, self.m_idx, 1, "month")
        self.day_label = self.create_selector("Day", self.days, self.d_idx, 2, "day")

        self.columns_frame.grid_columnconfigure((0,1,2), weight=1)

        # Summary and Finish
        self.summary_label = ctk.CTkLabel(self, text="", font=("Arial", 30), fg_color="gray20", corner_radius=10, width=400)
        self.summary_label.pack(pady=20)
        self.update_summary()

        self.ok_btn = ctk.CTkButton(self, text="Confirm & Next", width=400, height=90, 
                                   fg_color="#23d023", font=("Arial", 35),
                                   command=self.finish)
        self.ok_btn.pack(pady=20)

    def create_selector(self, title, items, start_idx, col, type_name):
        container = ctk.CTkFrame(self.columns_frame)
        container.grid(row=0, column=col, padx=10, sticky="nsew")
        
        ctk.CTkLabel(container, text=title, font=("Arial", 25, "bold")).pack(pady=5)
        
        # Up Button
        ctk.CTkButton(container, text="▲", width=120, height=70, font=("Arial", 30),
                      command=lambda: self.change_val(type_name, -1)).pack(pady=5)
        
        # The Current Selection Display
        lbl = ctk.CTkLabel(container, text=items[start_idx], font=("Arial", 40, "bold"), 
                           fg_color="gray30", corner_radius=5, width=120, height=80)
        lbl.pack(pady=10)
        
        # Down Button
        ctk.CTkButton(container, text="▼", width=120, height=70, font=("Arial", 30),
                      command=lambda: self.change_val(type_name, 1)).pack(pady=5)
        
        return lbl

    def change_val(self, type_name, delta):
        if type_name == "year":
            self.y_idx = (self.y_idx + delta) % len(self.years)
            self.year_label.configure(text=self.years[self.y_idx])
        elif type_name == "month":
            self.m_idx = (self.m_idx + delta) % len(self.months)
            self.month_label.configure(text=self.months[self.m_idx])
        elif type_name == "day":
            self.d_idx = (self.d_idx + delta) % len(self.days)
            self.day_label.configure(text=self.days[self.d_idx])
        
        self.update_summary()

    def update_summary(self):
        date_str = f"{self.years[self.y_idx]}-{self.months[self.m_idx]}-{self.days[self.d_idx]}"
        self.summary_label.configure(text=f"Selected: {date_str}")

    def finish(self):
        date_str = f"{self.years[self.y_idx]}-{self.months[self.m_idx]}-{self.days[self.d_idx]}"
        self.controller.current_item["expiry"] = date_str
        self.controller.show_frame("QuantityPage")

# Page 2.4: Quantity Input
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