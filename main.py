import tkinter as tk
from tkinter import ttk
from patient_tab import PatientTab
from doctor_tab import DoctorTab
from appointment_tab import AppointmentTab
from stay import StayTab
from room import RoomTab
from diagnosis import DiagnosisTab
from medicine import MedicineTab
from prescription import PrescriptionTab
from treatment import TreatmentTab
from billing import BillingTab
from receipt import ReceiptTab

class HospitalManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2D2F33")

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg="#252627", width=200)
        self.sidebar.pack(fill="y", side="left")

        # Sidebar Title
        self.sidebar_title = tk.Label(self.sidebar, text="Navigation", bg="#252627", fg="white", font=("Arial", 14))
        self.sidebar_title.pack(pady=10)

        # Create Navigation Buttons
        self.create_nav_buttons()

        # Main Content
        self.main_frame = tk.Frame(self.root, bg="#2D2F33")
        self.main_frame.pack(fill="both", expand=True)

        # Initialize tabs
        self.tabs = {
            "Patients": PatientTab(self.main_frame),
            "Doctors": DoctorTab(self.main_frame),
            "Appointments": AppointmentTab(self.main_frame),
            "Stays": StayTab(self.main_frame),
            "Rooms": RoomTab(self.main_frame),
            "Diagnoses": DiagnosisTab(self.main_frame),
            "Medicines": MedicineTab(self.main_frame),
            "Prescriptions": PrescriptionTab(self.main_frame),
            "Treatments": TreatmentTab(self.main_frame),
            "Billings": BillingTab(self.main_frame),
            "Receipts": ReceiptTab(self.main_frame)
        }

        # Start with the patient view
        self.show_tab("Patients")

    def create_nav_buttons(self):
        button_frame = tk.Frame(self.sidebar, bg="#252627")
        button_frame.pack(pady=10)

        # List of tab names
        tab_names = [
            "Patients", "Doctors", "Appointments", "Stays", "Rooms",
            "Diagnoses", "Medicines", "Prescriptions", "Treatments",
            "Billings", "Receipts"
        ]

        # Create buttons for each tab
        for tab_name in tab_names:
            button = tk.Button(button_frame, text=tab_name, bg="#1E90FF", fg="white", font=("Arial", 12),
                               command=lambda name=tab_name: self.show_tab(name))
            button.pack(fill="x", padx=5, pady=5)

    def show_tab(self, tab_name):
        # Hide all tabs
        for tab in self.tabs.values():
            tab.pack_forget()
        
        # Show the selected tab
        self.tabs[tab_name].pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalManagementSystem(root)
    root.mainloop()

    