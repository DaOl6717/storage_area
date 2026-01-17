from datetime import datetime
import customtkinter as ctk
import db_operations_backend as db_ops
import json

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.current_item = {
            "barcode": None,
            "name": None,
            "brand": None,
            "quantity": None,
            "location": None,
            "expiry": None
        }
        
        self.title("Pi Navigation System")
        self.attributes('-fullscreen', True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for PageClass in (MainMenu, AddPage, RemovePage, QuantityPage, NameInputPage, BrandInputPage, ExpiryInputPage, SpecifyLocation, ConfirmAddPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()
    
    def discard_and_home(self):
        for key in self.current_item:
            self.current_item[key] = None
    
        for frame in self.frames.values():
            if hasattr(frame, "clear"):
                frame.clear()
            
        self.show_frame("MainMenu")
        
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

        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(pady=10)

        ctk.CTkButton(ctrl_frame, text="«", width=120, height=70, font=("Arial", 40), fg_color="#d35400",
                      command=lambda: self.target_entry.delete(len(self.target_entry.get())-1, "end")).pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_frame, text="SPACE", width=300, height=70, font=("Arial", 32),
                      command=lambda: self.target_entry.insert("insert", " ")).pack(side="left", padx=5)

        ctk.CTkButton(ctrl_frame, text="»", width=120, font=("Arial", 40), height=70, fg_color="#23d023",
                      command=enter_command).pack(side="left", padx=5)

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

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Storage Management System", font=("Arial", 40)).pack(pady=30)
        
        add_button = ctk.CTkButton(self, text="Add Product", font=("Arial", 40), width=325, height=80,
                               command=lambda: controller.show_frame("AddPage"), fg_color="#23d023")
        add_button.pack(side='left', anchor='e', expand=True, pady=10, padx=10)

        remove_button = ctk.CTkButton(self, text="Remove Product", font=("Arial", 40), width=60, height=80,
                               command=lambda: controller.show_frame("RemovePage"), fg_color='#f72a2a')
        remove_button.pack(side='right', anchor='w', expand=True, pady=10, padx=10)

class AddPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Add Product", font=("Arial", 40)).pack(pady=30)
        ctk.CTkLabel(self, text="Please Scan Product", font=("Arial", 30)).pack(pady=60)
        
        self.barcode_entry = ctk.CTkEntry(self, width=600, height=80, font=("Arial", 30), justify="center")
        self.barcode_entry.pack(pady=0)
        self.barcode_entry.bind('<Return>', self.process_scan)
        
        back_btn = ctk.CTkButton(self, text="Cancel", fg_color="#f72a2a", command=controller.discard_and_home, width=120, height=60, font=("Arial", 30))
        back_btn.pack(pady=50)
        
        self.bind("<Visibility>", lambda e: self.barcode_entry.focus_set())
        
    def process_scan(self, event):
        barcode = self.barcode_entry.get().strip()
        self.controller.current_item["barcode"] = barcode
        
        if db_ops.barcode_exists(barcode):
            self.controller.show_frame("ExpiryInputPage")
        else:
            self.controller.show_frame("NameInputPage")

    def clear(self):
        self.barcode_entry.delete(0, 'end')
        
class NameInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        ctk.CTkLabel(self, text="Enter Product Name", font=("Arial", 40)).pack(pady=10)
        self.entry = ctk.CTkEntry(self, width=700, height=60, font=("Arial", 30), justify="center")
        self.entry.pack(pady=10)
        self.kb = TouchKeyboard(self, self.entry, self.next_step)
        self.kb.pack(pady=10)

    def next_step(self):
        self.controller.current_item["name"] = self.entry.get()
        self.controller.show_frame("BrandInputPage")
        
    def clear(self):
        self.entry.delete(0, 'end')

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
        self.controller.show_frame("ExpiryInputPage")
    
    def clear(self):
        self.entry.delete(0, 'end')

class ExpiryInputPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.years = [str(datetime.now().year + i) for i in range(11)]
        self.months = [f"{i:02d}" for i in range(1, 13)]
        self.days = [f"{i:02d}" for i in range(1, 32)]

        self.y_idx = 0
        self.m_idx = datetime.now().month - 1
        self.d_idx = 0

        ctk.CTkLabel(self, text="Select Expiry Date", font=("Arial", 40)).pack(pady=10)
        self.columns_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.columns_frame.pack(expand=True, fill="both", padx=20)

        self.year_label = self.create_selector("Year", self.years, self.y_idx, 0, "year")
        self.month_label = self.create_selector("Month", self.months, self.m_idx, 1, "month")
        self.day_label = self.create_selector("Day", self.days, self.d_idx, 2, "day")

        self.columns_frame.grid_columnconfigure((0,1,2), weight=1)

        self.ok_btn = ctk.CTkButton(self, text="Confirm & Next", width=400, height=90, 
                                   fg_color="#23d023", font=("Arial", 35),
                                   command=self.finish)
        self.ok_btn.pack(pady=20)

    def create_selector(self, title, items, start_idx, col, type_name):
        container = ctk.CTkFrame(self.columns_frame)
        container.grid(row=0, column=col, padx=10, sticky="nsew")
        ctk.CTkLabel(container, text=title, font=("Arial", 25, "bold")).pack(pady=5)
        ctk.CTkButton(container, text="▲", width=120, height=70, font=("Arial", 30),
                      command=lambda: self.change_val(type_name, -1)).pack(pady=5)
        lbl = ctk.CTkLabel(container, text=items[start_idx], font=("Arial", 40, "bold"), 
                           fg_color="gray30", corner_radius=5, width=120, height=80)
        lbl.pack(pady=10)
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

    def finish(self):
        date_str = f"{self.years[self.y_idx]}-{self.months[self.m_idx]}-{self.days[self.d_idx]}"
        self.controller.current_item["expiry"] = date_str
        self.controller.show_frame("QuantityPage")

class QuantityPage(ctk.CTkFrame):
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
        self.controller.show_frame("SpecifyLocation")
    
    def clear(self):
        self.entry.delete(0, 'end')

class SpecifyLocation(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Select Location", font=("Arial", 40)).pack(pady=30)
        ctk.CTkLabel(self, text="Please Scan Location ID", font=("Arial", 30)).pack(pady=60)
        self.barcode_entry = ctk.CTkEntry(self, width=600, height=80, font=("Arial", 30), justify="center")
        self.barcode_entry.pack(pady=0)
        self.barcode_entry.bind('<Return>', self.process_scan)
        back_btn = ctk.CTkButton(self, text="Cancel", fg_color="#f72a2a", command=controller.discard_and_home, width=120, height=60, font=("Arial", 30))
        back_btn.pack(pady=50)
        self.bind("<Visibility>", lambda e: self.barcode_entry.focus_set())
        
    def process_scan(self, event):
        barcode = self.barcode_entry.get().strip()
        self.controller.current_item["location"] = barcode
        self.controller.show_frame("ConfirmAddPage")
    
    def clear(self):
        self.barcode_entry.delete(0, 'end')

class ConfirmAddPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Summary", font=("Arial", 50, "bold")).pack(pady=20)
        self.data_container = ctk.CTkFrame(self, fg_color="transparent")
        self.data_container.pack(expand=True, fill="both", padx=40)
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="bottom", pady=40)
        self.back_btn = ctk.CTkButton(button_frame, text="Discard", width=250, height=90, 
                                      fg_color="#f72a2a", font=("Arial", 30),
                                      command=self.controller.discard_and_home)
        self.back_btn.pack(side="left", padx=20)
        self.finish_btn = ctk.CTkButton(button_frame, text="Finish", width=400, height=90, 
                                        fg_color="#23d023", font=("Arial", 35),
                                        command=self.send_to_system)
        self.finish_btn.pack(side="left", padx=20)

    def refresh(self):
        for widget in self.data_container.winfo_children():
            widget.destroy()
        data = self.controller.current_item
        display_names = {
            "barcode": "Barcode:", "name": "Product:", "brand": "Brand:",
            "quantity": "Quantity:", "location": "Location:", "expiry": "Expiry Date:"
        }
        row = 0
        for key, display_text in display_names.items():
            value = data.get(key)
            if value is not None and str(value).strip() != "":
                ctk.CTkLabel(self.data_container, text=display_text, font=("Arial", 25, "bold"), text_color="gray70").grid(row=row, column=0, sticky="e", padx=10, pady=5)
                ctk.CTkLabel(self.data_container, text=str(value), font=("Arial", 28)).grid(row=row, column=1, sticky="w", padx=10, pady=5)
                row += 1
        self.data_container.grid_columnconfigure((0,1), weight=1)

    def send_to_system(self):
        data = self.controller.current_item
        try:
            db_ops.add_inventory(
                quantity=data["quantity"],
                expiry_date=data["expiry"],
                barcode=data["barcode"],
                name=data["name"],
                brand=data["brand"],
                location_data=data["location"]
            )
            self.controller.discard_and_home() 
        except Exception as e:
            print(f"Error calling backend: {e}")

class RemovePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Remove Flow Not Implemented", font=("Arial", 24)).pack(pady=30)
        ctk.CTkButton(self, text="Back to Home", fg_color="gray30", command=controller.discard_and_home).pack(side="bottom", pady=20)