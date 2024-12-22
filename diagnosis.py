import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class DiagnosisTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#2D2F33")
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = tk.Frame(self, bg="#2D2F33")
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.search_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.search_frame.pack(side="top", fill="x", padx=10, pady=10)

        tk.Label(self.search_frame, text="Search by Diagnosis ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_diagnosis)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_diagnosis).pack(side="left", padx=5)

        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["AppointmentID", "DiagnosisDate", "DiagnosisDescription"]
        self.entries = {}
        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        self.create_styled_button(button_frame, "Add Diagnosis", self.add_diagnosis)
        self.create_styled_button(button_frame, "Update Diagnosis", self.update_diagnosis)
        self.create_styled_button(button_frame, "Delete Diagnosis", self.delete_diagnosis)

        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["DiagnosisID", "AppointmentID", "DiagnosisDate", "DiagnosisDescription"]
        self.tree_diagnosis = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_diagnosis.heading(col, text=col)
            self.tree_diagnosis.column(col, anchor="center", width=120)
        self.tree_diagnosis.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_diagnosis.bind("<Double-1>", lambda _: self.load_selected_diagnosis_row())
        self.refresh_diagnosis_treeview()

    def create_styled_button(self, parent, text, command):
        button = tk.Button(parent, text=text, bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=command)
        button.pack(side="left", padx=5)
        button.config(relief="flat", bd=0, highlightthickness=0)
        button.bind("<Enter>", lambda e: button.config(bg="#00BFFF"))
        button.bind("<Leave>", lambda e: button.config(bg="#1E90FF"))

    def search_diagnosis(self, event=None):
        search_id = self.search_entry.get()
        for item in self.tree_diagnosis.get_children():
            self.tree_diagnosis.delete(item)
        if search_id:
            for row in self.fetch_diagnoses():
                if str(row[0]) == search_id:
                    self.tree_diagnosis.insert("", "end", values=row)
        else:
            self.refresh_diagnosis_treeview()

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="hms"
        )

    def fetch_diagnoses(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Diagnosis")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_diagnosis(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "INSERT INTO Diagnosis (AppointmentID, DiagnosisDate, DiagnosisDescription) VALUES (%s, %s, %s)"
            cursor.execute(query, (data["AppointmentID"], data["DiagnosisDate"], data["DiagnosisDescription"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Diagnosis added successfully.")
            self.refresh_diagnosis_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def update_diagnosis(self):
        selected_item = self.tree_diagnosis.selection()
        if not selected_item:
            messagebox.showerror("Error", "No diagnosis selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        diagnosis_id = self.tree_diagnosis.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "UPDATE Diagnosis SET AppointmentID=%s, DiagnosisDate=%s, DiagnosisDescription=%s WHERE DiagnosisID=%s"
            cursor.execute(query, (data["AppointmentID"], data["DiagnosisDate"], data["DiagnosisDescription"], diagnosis_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Diagnosis updated successfully.")
            self.refresh_diagnosis_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_diagnosis(self):
        selected_item = self.tree_diagnosis.selection()
        if not selected_item:
            messagebox.showerror("Error", "No diagnosis selected!")
            return

        diagnosis_id = self.tree_diagnosis.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Diagnosis WHERE DiagnosisID=%s"
            cursor.execute(query, (diagnosis_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Diagnosis deleted successfully.")
            self.refresh_diagnosis_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_selected_diagnosis_row(self):
        selected_item = self.tree_diagnosis.selection()
        if not selected_item:
            messagebox.showerror("Error", "No diagnosis selected!")
            return
        data = self.tree_diagnosis.item(selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])

    def refresh_diagnosis_treeview(self):
        for item in self.tree_diagnosis.get_children():
            self.tree_diagnosis.delete(item)
        for row in self.fetch_diagnoses():
            self.tree_diagnosis.insert("", "end", values=row)