# main.py
# Entry point for the Storage Management System (FULL MQTT MODE)

import threading
import time

# Import your GUI
from gui import App

# Import your MQTT backend so it initializes the MQTT client
import db_operations_backend as backend


def main():
    print("Starting Storage Management System...")

    time.sleep(1)

    GUI = App()
    GUI.mainloop()


if __name__ == "__main__":
    main()