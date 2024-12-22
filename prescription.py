import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class PrescriptionTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Prescription ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_prescription)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_prescription).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["AppointmentID", "MedicineID", "Dosage", "Frequency", "Quantity", "StartDate", "EndDate"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Prescription", self.add_prescription)
        self.create_styled_button(button_frame, "Update Prescription", self.update_prescription)
        self.create_styled_button(button_frame, "Delete Prescription", self.delete_prescription)

        # Prescription Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["PrescriptionID", "AppointmentID", "MedicineID", "Dosage", "Frequency", "Quantity", "StartDate", "EndDate"]
        self.tree_prescription = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_prescription.heading(col, text=col)
            self.tree_prescription.column(col, anchor="center", width=120)
        self.tree_prescription.pack(fill="both", expand=True)

        # Styling for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_prescription.bind("<Double-1>", lambda _: self.load_selected_prescription_row())

        # Initial Data Load for Prescriptions
        self.refresh_prescription_treeview()

    def create_styled_button(self, parent, text, command):
        button = tk.Button(parent, text=text, bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command =command)
        button.pack(side="left", padx=5)
        button.config(relief="flat", borderwidth=0, highlightthickness=0)

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hms"
        )

    def fetch_prescriptions(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Prescription")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_prescription(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Check if AppointmentID and MedicineID exist
            cursor.execute("SELECT COUNT(*) FROM Appointment WHERE AppointmentID = %s", (data["AppointmentID"],))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Error", "Invalid AppointmentID.")
                return
            
            cursor.execute("SELECT COUNT(*) FROM Medicine WHERE MedicineID = %s", (data["MedicineID"],))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Error", "Invalid MedicineID.")
                return
            
            query = """
                INSERT INTO Prescription (AppointmentID, MedicineID, Dosage, Frequency, Quantity, StartDate, EndDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (data["AppointmentID"], data["MedicineID"], data["Dosage"], data["Frequency"], data["Quantity"], data["StartDate"], data["EndDate"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Prescription added successfully.")
            self.refresh_prescription_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def update_prescription(self):
        selected_item = self.tree_prescription.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a prescription to update.")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Check if AppointmentID and MedicineID exist
            cursor.execute("SELECT COUNT(*) FROM Appointment WHERE AppointmentID = %s", (data["AppointmentID"],))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Error", "Invalid AppointmentID.")
                return
            
            cursor.execute("SELECT COUNT(*) FROM Medicine WHERE MedicineID = %s", (data["MedicineID"],))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Error", "Invalid MedicineID.")
                return
            
            query = """
                UPDATE Prescription
                SET MedicineID = %s, Dosage = %s, Frequency = %s, Quantity = %s, StartDate = %s, EndDate = %s
                WHERE PrescriptionID = %s
            """
            cursor.execute(query, (data["MedicineID"], data["Dosage"], data["Frequency"], data["Quantity"], data["StartDate"], data["EndDate"], self.tree_prescription.item(selected_item)["values"][0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Prescription updated successfully.")
            self.refresh_prescription_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_prescription(self):
        selected_item = self.tree_prescription.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a prescription to delete.")
            return
        
        prescription_id = self.tree_prescription.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Prescription WHERE PrescriptionID = %s", (prescription_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Prescription deleted successfully.")
            self.refresh_prescription_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def refresh_prescription_treeview(self):
        for item in self.tree_prescription.get_children():
            self.tree_prescription.delete(item)
        for row in self.fetch_prescriptions():
            self.tree_prescription.insert("", "end", values=row)

    def load_selected_prescription_row(self):
        selected_item = self.tree_prescription.selection()
        if selected_item:
            values = self.tree_prescription.item(selected_item)["values"]
            for i, field in enumerate(self.entries):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[i])

    def search_prescription(self, event=None):
        search_term = self.search_entry.get()
        for item in self.tree_prescription.get_children():
            self.tree_prescription.delete(item)
        for row in self.fetch_prescriptions():
            if str(row[0]).startswith(search_term):  # Assuming PrescriptionID is the first column
                self.tree_prescription.insert("", "end", values=row)