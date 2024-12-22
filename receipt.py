import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class ReceiptTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Receipt ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_receipt)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_receipt).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["BillingID", "ReceiptDate", "TotalAmount", "TreatmentDetails", "MedicineDetails"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Receipt", self.add_receipt)
        self.create_styled_button(button_frame, "Update Receipt", self.update_receipt)
        self.create_styled_button(button_frame, "Delete Receipt", self.delete_receipt)

        # Receipt Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["ReceiptID", "BillingID", "ReceiptDate", "TotalAmount", "TreatmentDetails", "MedicineDetails"]
        self.tree_receipt = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_receipt.heading(col, text=col)
            self.tree_receipt.column(col, anchor="center", width=120)
        self.tree_receipt.pack(fill="both", expand=True)

        # Styling for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2D2F33", foreground="#E0E0E0", rowheight=25, fieldbackground="#2D2F33")
        style.map("Treeview", background=[("selected", "#3E4045")])
        style.configure("Treeview.Heading", background="#3A3B3E", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

        self.tree_receipt.bind("<Double-1>", lambda _: self.load_selected_receipt_row())

        # Initial Data Load for Receipts
        self.refresh_receipt_treeview()

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

    def fetch_receipts(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Receipt")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_receipt(self, event=None):
        search_term = self.search_entry.get()
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Receipt WHERE ReceiptID LIKE %s", (f"%{search_term}%",))
        rows = cursor.fetchall()
        conn.close()
        self.update_receipt_treeview(rows)

    def update_receipt_treeview(self, rows):
        for item in self.tree_receipt.get_children():
            self.tree_receipt.delete(item)
        for row in rows:
            self.tree_receipt.insert("", "end", values=row)

    def add_receipt(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Check if BillingID exists
            cursor.execute("SELECT COUNT(*) FROM Billing WHERE BillingID = %s", (data["BillingID"],))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Error", "Invalid BillingID.")
                return
            
            query = """
                INSERT INTO Receipt (BillingID, ReceiptDate, TotalAmount, TreatmentDetails, MedicineDetails)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (data["BillingID"], data["ReceiptDate"], data["TotalAmount"], data["TreatmentDetails"], data["MedicineDetails"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Receipt added successfully.")
            self.refresh_receipt_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def update_receipt(self):
        selected_item = self.tree_receipt.selection()
        if not selected_item:
            messagebox.showerror("Error", "No receipt selected!")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        receipt_id = self.tree_receipt.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            # Check if BillingID exists
            cursor.execute("SELECT COUNT(*) FROM Billing WHERE BillingID = %s", (data["BillingID"],))
            if cursor.fetchone()[0] == 0:
                messagebox.showerror("Error", "Invalid BillingID.")
                return
            
            query = """
                UPDATE Receipt
                SET BillingID=%s, ReceiptDate=%s, TotalAmount=%s, TreatmentDetails=%s, MedicineDetails=%s
                WHERE ReceiptID=%s
            """
            cursor.execute(query, (data["BillingID"], data["ReceiptDate"], data["TotalAmount"], data["TreatmentDetails"], data["MedicineDetails"], receipt_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Receipt updated successfully.")
            self.refresh_receipt_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_receipt(self):
        selected_item = self.tree_receipt.selection()
        if not selected_item:
            messagebox.showerror("Error", "No receipt selected!")
            return

        receipt_id = self.tree_receipt.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM Receipt WHERE ReceiptID=%s"
            cursor.execute(query, (receipt_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Receipt deleted successfully.")
            self.refresh_receipt_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def load_selected_receipt_row(self):
        selected_item = self.tree_receipt.selection()
        if not selected_item:
            messagebox.showerror("Error", "No receipt selected!")
            return
        data = self.tree_receipt.item(selected_item)["values"]
        for i, field in enumerate(self.entries):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, data[i + 1])  # Skip ReceiptID

    def refresh_receipt_treeview(self):
        for item in self.tree_receipt.get_children():
            self.tree_receipt.delete(item)
        for row in self.fetch_receipts():
            self.tree_receipt.insert("", "end", values=row)