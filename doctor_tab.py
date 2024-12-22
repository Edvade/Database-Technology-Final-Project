import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re

class DoctorTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#2D2F33")
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self, bg="#2D2F33")
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.search_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.search_frame.pack(side="top", fill="x", padx=10, pady=10)

        tk.Label(self.search_frame, text="Search by Name or Specialty:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_doctor)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_doctor).pack(side="left", padx=5)

        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["FirstName", "LastName", "Specialty", "PhoneNumber", "Email", "LicenseNumber", "YearsOfExperience"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.entries[field] = entry

        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Doctor", self.add_doctor)
        self.create_styled_button(button_frame, "Update Doctor", self.update_doctor)
        self.create_styled_button(button_frame, "Delete Doctor", self.delete_doctor)

        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["DoctorID", "FirstName", "LastName", "Specialty", "PhoneNumber", "Email", "LicenseNumber", "YearsOfExperience"]
        self.tree_doctor = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=8)
        self.tree_doctor.pack(side="left", fill="both", expand=True)

        for col in columns:
            self.tree_doctor.heading(col, text=col)
            self.tree_doctor.column(col, anchor="center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree_doctor.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_doctor.configure(yscroll=scrollbar.set)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_doctor.bind("<Double-1>", lambda _: self.load_selected_doctor_row())
        self.refresh_doctor_treeview()

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hms"
        )

    def fetch_doctors(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Doctor")
        rows = cursor .fetchall()
        conn.close()
        return rows

    def search_doctor(self, event=None):
        search_term = self.search_entry.get().lower()
        conn = self.connect_db()
        cursor = conn.cursor()
        query = """
            SELECT * FROM Doctor
            WHERE LOWER(FirstName) LIKE %s OR LOWER(LastName) LIKE %s OR LOWER(Specialty) LIKE %s
        """
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = cursor.fetchall()
        conn.close()
        self.update_treeview(rows)

    def update_treeview(self, rows):
        for item in self.tree_doctor.get_children():
            self.tree_doctor.delete(item)
        for row in rows:
            self.tree_doctor.insert("", "end", values=row)

    def add_doctor(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        # Validate phone number format
        if not re.match(r'^\+?\d{10,15}$', data["PhoneNumber"]):
            messagebox.showerror("Error", "Phone number must be between 10 to 15 digits.")
            return
        
        # Validate email format
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data["Email"]):
            messagebox.showerror("Error", "Invalid email format.")
            return
        
        # Validate years of experience
        if not data["YearsOfExperience"].isdigit() or int(data["YearsOfExperience"]) < 0:
            messagebox.showerror("Error", "Years of experience must be a non-negative integer.")
            return

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Doctor (FirstName, LastName, Specialty, PhoneNumber, Email, LicenseNumber, YearsOfExperience)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Doctor added successfully.")
            self.refresh_doctor_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def update_doctor(self):
        selected_item = self.tree_doctor.selection()
        if not selected_item:
            messagebox.showerror("Error", "No doctor selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        doctor_id = self.tree_doctor.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Doctor
                SET FirstName=%s, LastName=%s, Specialty=%s, PhoneNumber=%s, Email=%s, LicenseNumber=%s, YearsOfExperience=%s
                WHERE DoctorID=%s
            """
            cursor.execute(query, (*data.values(), doctor_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Doctor updated successfully.")
            self.refresh_doctor_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_doctor(self):
        selected_item = self.tree_doctor.selection()
        if not selected_item:
            messagebox.showerror("Error", "No doctor selected!")
            return

        doctor_id = self.tree_doctor.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Doctor WHERE DoctorID=%s"
            cursor.execute(query, (doctor_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Doctor deleted successfully.")
            self.refresh_doctor_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_selected_doctor_row(self):
        selected_item = self.tree_doctor.selection()
        if not selected_item:
            messagebox.showerror("Error", "No doctor selected!")
            return
        
        data = self.tree_doctor.item(selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])  # Skip DoctorID

    def refresh_doctor_treeview(self):
        for item in self.tree_doctor.get_children ():
            self.tree_doctor.delete(item)
        for row in self.fetch_doctors():
            self.tree_doctor.insert("", "end", values=row)

    def create_styled_button(self, parent, text, command):
        button =  tk.Button(parent, text=text, bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=command)
        button.pack(side="left", padx=5)
        button.config(relief="flat", bd=0, highlightthickness=0)
        button.bind("<Enter>", lambda e: button.config(bg="#00BFFF"))
        button.bind("<Leave>", lambda e: button.config(bg="#1E90FF"))