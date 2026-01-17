import threading
import time
from gui import App
import db_operations_backend as backend

def main():
    print("Starting Storage Management System...")
    time.sleep(1)
    GUI = App()
    GUI.mainloop()

if __name__ == "__main__":
    main()