import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class StayTab(tk.Frame):
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
        self.search_entry.bind("<KeyRelease>", self.search_stay)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_stay).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["AppointmentID", "RoomID", "DaysStayed"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Stay", self.add_stay)
        self.create_styled_button(button_frame, "Update Stay", self.update_stay)
        self.create_styled_button(button_frame, "Delete Stay", self.delete_stay)

        # Stay Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["StayID", "AppointmentID", "RoomID", "DaysStayed"]
        self.tree_stay = ttk.Treeview(self.tree_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree_stay.heading(col, text=col)
            self.tree_stay.column(col, anchor="center", width=120)
        self.tree_stay.pack(fill="both", expand=True)

        # Initial Data Load for Stays
        self.refresh_stay_treeview()

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

    def fetch_stays(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Stay")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_stay(self, event=None):
        search_value = self.search_entry.get()
        conn = self.connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM Stay WHERE AppointmentID LIKE %s"
        cursor.execute(query, (f"%{search_value}%",))
        rows = cursor.fetchall()
        conn.close()
        
        for item in self.tree_stay.get_children():
            self.tree_stay.delete(item)
        for row in rows:
            self.tree_stay.insert("", "end", values=row)

    def add_stay(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        if not data["DaysStayed"].isdigit() or int(data["DaysStayed"]) <= 0:
            messagebox.showerror("Error", "Days Stayed must be a positive integer.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Stay (AppointmentID, RoomID, DaysStayed)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (data["AppointmentID"], data["RoomID"], data["DaysStayed"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Stay added successfully.")
            self.refresh_stay_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def update_stay(self):
        selected_item = self.tree_stay.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a stay to update.")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        if not data["DaysStayed"].isdigit() or int(data["DaysStayed"]) <= 0:
            messagebox.showerror("Error", "Days Stayed must be a positive integer.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Stay
                SET RoomID = %s, DaysStayed = %s
                WHERE AppointmentID = %s AND StayID = %s
            """
            cursor.execute(query, (data["RoomID"], data["DaysStayed"], data["AppointmentID"], self.tree_stay.item(selected_item)["values"][0]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Stay updated successfully.")
            self.refresh_stay_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_stay(self):
        selected_item = self.tree_stay.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a stay to delete.")
            return
        
        stay_id = self.tree_stay.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Stay WHERE StayID = %s", (stay_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Stay deleted successfully.")
            self.refresh_stay_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def refresh_stay_treeview(self):
        for item in self.tree_stay.get_children():
            self.tree_stay.delete(item)
        for row in self.fetch_stays():
            self.tree_stay.insert("", "end", values=row)

    def load_selected_stay_row(self):
        selected_item = self.tree_stay.selection()
        if selected_item:
            values = self.tree_stay.item(selected_item)["values"]
            for i, field in enumerate(self.entries):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[i])