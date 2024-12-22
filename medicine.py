import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class MedicineTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Medicine Name:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_medicine)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_medicine).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["MedicineName", "MethodofAdmin", "Manufacturer", "Price"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Medicine", self.add_medicine)
        self.create_styled_button(button_frame, "Update Medicine", self.update_medicine)
        self.create_styled_button(button_frame, "Delete Medicine", self.delete_medicine)

        # Medicine Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["MedicineID", "MedicineName", "MethodofAdmin", "Manufacturer", "Price"]
        self.tree_medicine = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_medicine.heading(col, text=col)
            self.tree_medicine.column(col, anchor="center", width=120)
        self.tree_medicine.pack(fill="both", expand=True)

        # Styling for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_medicine.bind("<Double-1>", lambda _: self.load_selected_medicine_row())

        # Initial Data Load for Medicines
        self.refresh_medicine_treeview()

    def create_styled_button(self, parent, text, command):
        button = tk.Button(parent, text=text, bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=command)
        button.pack(side="left", padx=5)
        button.config(relief="flat", borderwidth=0, highlightthickness=0)

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost",
            user=" root",
            password="root",
            database="hms"
        )

    def fetch_medicines(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Medicine")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_medicine(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Check for duplicate medicine
            cursor.execute("SELECT COUNT(*) FROM Medicine WHERE MedicineName = %s", (data["MedicineName"],))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "This medicine already exists.")
                return
            
            query = """
                INSERT INTO Medicine (MedicineName, MethodofAdmin, Manufacturer, Price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (data["MedicineName"], data["MethodofAdmin"], data["Manufacturer"], data["Price"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Medicine added successfully.")
            self.refresh_medicine_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def update_medicine(self):
        selected_item = self.tree_medicine.selection()
        if not selected_item:
            messagebox.showerror("Error", "No medicine selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        medicine_id = self.tree_medicine.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Ensure price is unique for the medicine
            cursor.execute("SELECT COUNT(*) FROM Medicine WHERE MedicineName = %s AND MedicineID != %s", (data["MedicineName"], medicine_id))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "This medicine name already exists with a different ID.")
                return
            
            query = """
                UPDATE Medicine
                SET MedicineName=%s, MethodofAdmin=%s, Manufacturer=%s, Price=%s
                WHERE MedicineID=%s
            """
            cursor.execute(query, (data["MedicineName"], data["MethodofAdmin"], data["Manufacturer"], data["Price"], medicine_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Medicine updated successfully.")
            self.refresh_medicine_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def delete_medicine(self):
        selected_item = self.tree_medicine.selection()
        if not selected_item:
            messagebox.showerror("Error", "No medicine selected!")
            return

        medicine_id = self.tree_medicine.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Medicine WHERE MedicineID=%s"
            cursor.execute(query, (medicine_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Medicine deleted successfully.")
            self.refresh_medicine_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def load_selected_medicine_row(self):
        selected_item = self.tree_medicine.selection()
        if not selected_item:
            messagebox.showerror("Error", "No medicine selected!")
            return
        data = self.tree_medicine.item(selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])  # Skip MedicineID

    def refresh_medicine_treeview(self):
        for item in self.tree_medicine.get_children():
            self.tree_medicine.delete(item)
        for row in self.fetch_medicines():
            self.tree_medicine.insert("", "end", values=row)

    def search_medicine(self, event=None):
        search_term = self.search_entry.get().lower()
        for item in self.tree_medicine.get_children():
            self.tree_medicine.delete(item)
        for row in self.fetch_medicines():
            if search_term in row[1].lower():
                self.tree_medicine.insert("", "end", values=row)