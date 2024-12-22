import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class AppointmentTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Appointment ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_appointment)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_appointment).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Updated fields in the correct order
        fields = ["PatientID", "DoctorID", "AppointmentDate", "AppointmentTime", "Notes", "Status"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Appointment", self.add_appointment)
        self.create_styled_button(button_frame, "Update Appointment", self.update_appointment)
        self.create_styled_button(button_frame, "Delete Appointment", self.delete_appointment)

        # Appointment Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["AppointmentID", "PatientID", "DoctorID", "AppointmentDate", "AppointmentTime", "Notes", "Status"]
        self.tree_appointment = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_appointment.heading(col, text=col)
            self.tree_appointment.column(col, anchor="center", width=120)
        self.tree_appointment.pack(fill="both", expand=True)

        # Styling for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_appointment.bind("<Double-1>", lambda _: self.load_selected_appointment_row())

        # Initial Data Load for Appointments
        self.refresh_appointment_treeview()

    def create_styled_button(self, parent, text, command):
        button = tk.Button(parent, text=text, bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command =command)
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

    def fetch_appointments(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Appointment")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_appointment(self, event=None):
        search_term = self.search_entry.get()
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Appointment WHERE AppointmentID LIKE %s", (f"%{search_term}%",))
        rows = cursor.fetchall()
        conn.close()
        self.update_appointment_treeview(rows)

    def update_appointment_treeview(self, rows):
        for item in self.tree_appointment.get_children():
            self.tree_appointment.delete(item)
        for row in rows:
            self.tree_appointment.insert("", "end", values=row)

    def add_appointment(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        # Check for overlapping appointments
        if self.check_overlapping_appointments(data["DoctorID"], data["AppointmentDate"], data["AppointmentTime"]):
            messagebox.showerror("Error", "This doctor already has an appointment at the selected date and time.")
            return

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime, Notes, Status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Appointment added successfully.")
            self.refresh_appointment_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def check_overlapping_appointments(self, doctor_id, appointment_date, appointment_time):
        conn = self.connect_db()
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) FROM Appointment
            WHERE DoctorID = %s AND AppointmentDate = %s AND AppointmentTime = %s
        """
        cursor.execute(query, (doctor_id, appointment_date, appointment_time))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def update_appointment(self):
        selected_item = self.tree_appointment.selection()
        if not selected_item:
            messagebox.showerror("Error", "No appointment selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        appointment_id = self.tree_appointment.item(selected_item)["values"][0]
        
        # Check for overlapping appointments
        if self.check_overlapping_appointments(data["DoctorID"], data["AppointmentDate"], data["AppointmentTime"]):
            messagebox.showerror("Error", "This doctor already has an appointment at the selected date and time.")
            return

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Appointment
                SET PatientID=%s, DoctorID=%s, AppointmentDate=%s, AppointmentTime=%s, Notes=%s, Status=%s
                WHERE AppointmentID=%s
            """
            cursor.execute(query, (*data.values(), appointment_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Appointment updated successfully.")
            self.refresh_appointment_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_appointment(self):
        selected_item = self.tree_appointment.selection()
        if not selected_item:
            messagebox.showerror("Error", "No appointment selected!")
            return

        appointment_id = self.tree_appointment.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Appointment WHERE AppointmentID=%s"
            cursor.execute(query, (appointment_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Appointment deleted successfully.")
            self.refresh_appointment_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_selected_appointment_row(self):
        selected_item = self.tree_appointment.selection()
        if not selected_item:
            messagebox.showerror("Error", "No appointment selected!")
            return
        data = self.tree_appointment.item(selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])  # Skip AppointmentID

    def refresh_appointment_treeview(self):
        for item in self.tree_appointment.get_children():
            self.tree_appointment.delete(item)
        for row in self.fetch_appointments():
            self.tree_appointment.insert("", "end", values=row)