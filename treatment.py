import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class TreatmentTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Treatment ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_treatment)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_treatment).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Fields in the correct order
        fields = ["DiagnosisID", "TreatmentDescription", "TreatmentDate", "DoctorID", "Price", "Status"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Treatment", self.add_treatment)
        self.create_styled_button(button_frame, "Update Treatment", self.update_treatment)
        self.create_styled_button(button_frame, "Delete Treatment", self.delete_treatment)

        # Treatment Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["TreatmentID", "DiagnosisID", "TreatmentDescription", "TreatmentDate", "DoctorID", "Price", "Status"]
        self.tree_treatment = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_treatment.heading(col, text=col)
            self.tree_treatment.column(col, anchor="center", width=120)
        self.tree_treatment.pack(fill="both", expand=True)

        # Styling for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_treatment.bind("<Double-1 >", lambda _: self.load_selected_treatment_row())

        # Initial Data Load for Treatments
        self.refresh_treatment_treeview()

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

    def fetch_treatments(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Treatment")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_treatment(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        if not data["Price"].replace('.', '', 1).isdigit() or float(data["Price"]) < 0:
            messagebox.showerror("Error", "Price must be a non-negative number.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Treatment (DiagnosisID, TreatmentDate, TreatmentDescription, DoctorID, Price, Status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (data["DiagnosisID"], data["TreatmentDate"], data["TreatmentDescription"], data["DoctorID"], data["Price"], data["Status"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Treatment added successfully.")
            self.refresh_treatment_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def update_treatment(self):
        selected_item = self.tree_treatment.selection()
        if not selected_item:
            messagebox.showerror("Error", "No treatment selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        if not data["Price"].replace('.', '', 1).isdigit() or float(data["Price"]) < 0:
            messagebox.showerror("Error", "Price must be a non-negative number.")
            return

        treatment_id = self.tree_treatment.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Treatment
                SET DiagnosisID=%s, TreatmentDate=%s, TreatmentDescription=%s, DoctorID=%s, Price=%s, Status=%s
                WHERE TreatmentID=%s
            """
            cursor.execute(query, (data["DiagnosisID"], data["TreatmentDate"], data["TreatmentDescription"], data["DoctorID"], data["Price"], data["Status"], treatment_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Treatment updated successfully.")
            self.refresh_treatment_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_treatment(self):
        selected_item = self.tree_treatment.selection()
        if not selected_item:
            messagebox.showerror("Error", "No treatment selected!")
            return

        treatment_id = self.tree_treatment.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Treatment WHERE TreatmentID=%s"
            cursor.execute(query, (treatment_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Treatment deleted successfully.")
            self.refresh_treatment_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def load_selected_treatment_row(self):
        selected_item = self.tree_treatment.selection()
        if not selected_item:
            messagebox.showerror("Error", "No treatment selected!")
            return
        data = self.tree_treatment.item(selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])  # Skip Treatment ID

    def refresh_treatment_treeview(self):
        for item in self.tree_treatment.get_children():
            self.tree_treatment.delete(item)
        for row in self.fetch_treatments():
            self.tree_treatment.insert("", "end", values=row)

    def search_treatment(self, event=None):
        search_id = self.search_entry.get()
        for item in self.tree_treatment.get_children():
            self.tree_treatment.delete(item)
        if search_id:
            for row in self.fetch_treatments():
                if str(row[0]) == search_id:
                    self.tree_treatment.insert("", "end", values=row)
        else:
            self.refresh_treatment_treeview() 