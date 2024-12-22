import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class RoomTab(tk.Frame):
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

        tk.Label(self.search_frame, text="Search by Room ID:", bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).pack(side="left", padx=5)
        self.search_entry = tk.Entry(self.search_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_room)
        tk.Button(self.search_frame, text="Search", bg="#1E90FF", fg="white", font=("Helvetica", 10, "bold"), command=self.search_room).pack(side="left", padx=5)

        # Form Frame
        self.form_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.form_frame.pack(side="top", fill="x", padx=10, pady=10)

        fields = ["RoomID", "RoomType", "PricePerDay"]
        self.entries = {}

        for i, field in enumerate(fields):
            tk.Label(self.form_frame, text=field, bg="#2D2F33", fg="#FFFFFF", font=("Helvetica", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=10)
            entry = tk.Entry(self.form_frame, bg="#3A3B3E", fg="#E0E0E0", insertbackground="#FFFFFF", font=("Helvetica", 10))
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.entries[field] = entry

        # Button Section
        button_frame = tk.Frame(self.form_frame, bg="#2D2F33")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        self.create_styled_button(button_frame, "Add Room", self.add_room)
        self.create_styled_button(button_frame, "Update Room", self.update_room)
        self.create_styled_button(button_frame, "Delete Room", self.delete_room)

        # Room Table Section
        self.tree_frame = tk.Frame(self.main_frame, bg="#2D2F33")
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ["RoomID", "RoomType", "PricePerDay"]
        self.tree_room = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=8)
        self.tree_room.pack(side="left", fill="both", expand=True)

        for col in columns:
            self.tree_room.heading(col, text=col)
            self.tree_room.column(col, anchor="center")

        # Initial Data Load for Rooms
        self.refresh_room_treeview()

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

    def fetch_rooms(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Room")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_room(self):
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error ", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO Room (RoomID, RoomType, PricePerDay)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (data["RoomID"], data["RoomType"], data["PricePerDay"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Room added successfully.")
            self.refresh_room_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def update_room(self):
        selected_item = self.tree_room.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a room to update.")
            return
        
        data = {field: self.entries[field].get() for field in self.entries}
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            query = """
                UPDATE Room
                SET RoomType = %s, PricePerDay = %s
                WHERE RoomID = %s
            """
            cursor.execute(query, (data["RoomType"], data["PricePerDay"], data["RoomID"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Room updated successfully.")
            self.refresh_room_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def delete_room(self):
        selected_item = self.tree_room.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a room to delete.")
            return
        
        room_id = self.tree_room.item(selected_item)["values"][0]
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Room WHERE RoomID = %s", (room_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Room deleted successfully.")
            self.refresh_room_treeview()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def refresh_room_treeview(self):
        for item in self.tree_room.get_children():
            self.tree_room.delete(item)
        for row in self.fetch_rooms():
            self.tree_room.insert("", "end", values=row)

    def search_room(self, event=None):
        search_term = self.search_entry.get().lower()
        for item in self.tree_room.get_children():
            self.tree_room.delete(item)
        for row in self.fetch_rooms():
            if search_term in row[0].lower():  # Assuming RoomID is the first column
                self.tree_room.insert("", "end", values=row)

    def load_selected_room_row(self):
        selected_item = self.tree_room.selection()
        if selected_item:
            values = self.tree_room.item(selected_item)["values"]
            for i, field in enumerate(self.entries):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, values[i])