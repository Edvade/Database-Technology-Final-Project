import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class BillingTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Billing ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_billing)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_billing).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["AppointmentID", "PaymentDate", "PaymentMethod", "Status"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Billing", self.add_billing)
        self.create_styled_button(button_frame, "Update Billing", self.update_billing)
        self.create_styled_button(button_frame, "Delete Billing", self.delete_billing)

        # Billing Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["BillingID", "AppointmentID", "TotalAmount", "PaymentDate", "PaymentMethod", "Status"]
        self.billing_tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.billing_tree.heading(col, text=col)
            self.billing_tree.column(col, anchor="center", width=120)
        self.billing_tree.pack(fill="both", expand=True)

        # Initial Data Load for Billing
        self.refresh_billing_treeview()

        # Bind double-click to load selected billing row
        self.billing_tree.bind("<Double-1>", lambda _: self.load_selected_billing_row())

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

    def fetch_billing(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Billing")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_billing(self, event=None):
        search_term = self.search_entry.get()
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Billing WHERE BillingID LIKE %s", (f"%{search_term}%",))
        rows = cursor.fetchall()
        conn.close()
        self.update_billing_treeview(rows)

    def update_billing_treeview(self, rows):
        for item in self.billing_tree.get_children():
            self.billing_tree.delete(item)
        for row in rows:
            self.billing_tree.insert("", "end", values=row)

    def calculate_total_amount(self, appointment_id):
        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT T.Price FROM Treatment T
            JOIN Diagnosis D ON T.DiagnosisID = D.DiagnosisID
            WHERE D.AppointmentID = %s
        """, (appointment_id,))
        treatment_price = cursor.fetchone()
        treatment_price = treatment_price[0] if treatment_price else 0

        cursor.execute("""
            SELECT SUM(M.Price * P.Quantity) FROM Prescription P
            JOIN Medicine M ON P.MedicineID = M.MedicineID
            WHERE P.AppointmentID = %s
        """, (appointment_id,))
        medicine_total = cursor.fetchone()
        medicine_total = medicine_total[0] if medicine_total else 0

        cursor.execute("""
            SELECT R.PricePerDay, S.DaysStayed FROM Stay S
            JOIN Room R ON S.RoomID = R.RoomID
            WHERE S.AppointmentID = %s
        """, (appointment_id,))
        room_total = 0
        for room_price, days in cursor.fetchall():
            room_total += room_price * days

        conn.close()
        total_amount = treatment_price + (medicine_total if medicine_total else 0) + room_total
        return total_amount

    def add_billing(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            appointment_id = int(data["AppointmentID"])
            total_amount = self.calculate_total_amount(appointment_id)

            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Billing (AppointmentID, TotalAmount, PaymentDate, PaymentMethod, Status)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (appointment_id, total_amount, data["PaymentDate"], data["PaymentMethod"], data["Status"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Billing added successfully.")
            self.refresh_billing_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def update_billing(self):
        selected_item = self.billing_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a billing record to update.")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        billing_id = self.billing_tree.item(selected_item)["values"][0]
        try:
            appointment_id = int(data["AppointmentID"])
            total_amount = self.calculate_total_amount(appointment_id)

            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Billing
                SET AppointmentID = %s, TotalAmount = %s, PaymentDate = %s, PaymentMethod = %s, Status = %s
                WHERE BillingID = %s
            """
            cursor.execute(query, (appointment_id, total_amount, data["PaymentDate"], data["PaymentMethod"], data["Status"], billing_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Billing updated successfully.")
            self.refresh_billing_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_billing(self):
        selected_item = self.billing_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a billing record to delete.")
            return
        
        billing_id = self.billing_tree.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Billing WHERE BillingID = %s", (billing_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Billing deleted successfully.")
            self.refresh_billing_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err }")

    def refresh_billing_treeview(self):
        for item in self.billing_tree.get_children():
            self.billing_tree.delete(item)
        for row in self.fetch_billing():
            self.billing_tree.insert("", "end", values=row)

    def load_selected_billing_row(self):
        selected_item = self.billing_tree.selection()
        if selected_item:
            values = self.billing_tree.item(selected_item)["values"]
            for i, field in enumerate(self.entries):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[i + 1])