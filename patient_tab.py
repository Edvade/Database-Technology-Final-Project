import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class PatientTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#2D2F33")
        self.create_widgets()

    def create_widgets(self):
        # Main Frame
        self.main_frame = tk.Frame(self, bg="#2D2F33")
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Search Bar
        self.search_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.search_frame.pack(side="top", fill="x", padx=10, pady=10)

        tk.Label(self.search_frame, text="Search by Patient Name:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_patient)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_patient).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["FirstName", "LastName", "DateOfBirth", "Gender", "Address", "PhoneNumber", "Email", "InsuranceProvider", "InsurancePolicyNumber", "EmergencyContactName", "EmergencyContactPhone"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Patient", self.add_patient)
        self.create_styled_button(button_frame, "Update Patient", self.update_patient)
        self.create_styled_button(button_frame, "Delete Patient", self.delete_patient)

        # Patient Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["PatientID", "FirstName", "LastName", "DateOfBirth", "Gender", "Address", "PhoneNumber", "Email", "InsuranceProvider", "InsurancePolicyNumber", "EmergencyContactName", "EmergencyContactPhone"]
        self.tree_patient = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_patient.heading(col, text=col)
            self.tree_patient.column(col, anchor="center", width=120)
        self.tree_patient.pack(fill="both", expand=True)

        # Styling for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_patient.bind("<Double-1>", lambda _: self.load_selected_patient_row())

        # Initial Data Load for Patients
        self.refresh_patient_treeview()

    def create_styled_button(self, parent, text, command):
        button = tk.Button(parent, text=text, bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=command)
        button.pack(side="left", padx=5)
        button.config(relief="flat", bd=0, highlightthickness=0)
        button.bind("<Enter>", lambda e: button.config(bg="#00BFFF"))
        button.bind("<Leave>", lambda e: button.config(bg="#1E90FF"))

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hms"
        )

    def fetch_patients(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patient")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_patient(self, event=None):
        search_term = self.search_entry.get()
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patient WHERE FirstName LIKE %s OR LastName LIKE %s", (f"%{search_term}%", f"%{search_term}%"))
        rows = cursor.fetchall()
        conn.close()
        self.update_patient_treeview(rows)

    def update_patient_treeview(self, rows):
        for item in self.tree_patient.get_children():
            self.tree_patient.delete(item)
        for row in rows:
            self.tree_patient.insert("", "end", values=row)

    def add_patient(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Check for duplicate patient
            cursor.execute("SELECT COUNT(*) FROM Patient WHERE FirstName = %s AND LastName = %s AND DateOfBirth = %s", 
                           (data["FirstName"], data["LastName"], data["DateOfBirth"]))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "This patient already exists.")
                return
            
            query = """
                INSERT INTO Patient (FirstName, LastName, DateOfBirth, Gender, Address, PhoneNumber, Email, InsuranceProvider, InsurancePolicyNumber, EmergencyContactName, EmergencyContactPhone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Patient added successfully.")
            self.refresh_patient_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def update_patient(self):
        selected_item = self.tree_patient.selection()
        if not selected_item:
            messagebox.showerror("Error", "No patient selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        patient_id = self.tree_patient.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Patient
                SET FirstName=%s, LastName=%s, DateOfBirth=%s, Gender=%s, Address=%s, PhoneNumber=%s, Email=%s, InsuranceProvider=%s, InsurancePolicyNumber=%s, EmergencyContactName=%s, EmergencyContactPhone=%s
                WHERE PatientID=%s
            """
            cursor.execute(query, (*data.values(), patient_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Patient updated successfully.")
            self.refresh_patient_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_patient(self):
        selected_item = self.tree_patient.selection()
        if not selected_item:
            messagebox.showerror("Error", "No patient selected!")
            return

        patient_id = self.tree_patient.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Patient WHERE PatientID=%s"
            cursor.execute(query, (patient_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Patient deleted successfully.")
            self.refresh_patient_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_selected_patient_row(self):
        selected_item = self.tree_patient.selection()
        if not selected_item:
            messagebox.showerror("Error", "No patient selected!")
            return
        
        data = self.tree_patient.item (selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])  # Skip PatientID

    def refresh_patient_treeview(self):
        for item in self.tree_patient.get_children():
            self.tree_patient.delete(item)
        for row in self.fetch_patients():
            self.tree_patient.insert("", "end", values=row)