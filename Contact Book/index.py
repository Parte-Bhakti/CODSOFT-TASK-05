import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ContactBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("600x500")
        self.root.configure(bg="#F0F8FF")

        # Database setup
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        # UI Layout
        title = tk.Label(root, text="Contact Book", font=("Arial", 20, "bold"), bg="#F0F8FF", fg="#333")
        title.pack(pady=10)

        form_frame = tk.Frame(root, bg="#F0F8FF")
        form_frame.pack(pady=5)

        # Form labels and entries
        self.entries = {}
        fields = [("Name", 0), ("Phone", 1), ("Email", 2), ("Address", 3)]
        for label, row in fields:
            tk.Label(form_frame, text=f"{label}:", font=("Arial", 12), bg="#F0F8FF").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.entries[label.lower()] = entry

        # Buttons
        button_frame = tk.Frame(root, bg="#F0F8FF")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Contact", width=15, command=self.add_contact, bg="#87CEFA", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Contact", width=15, command=self.update_contact, bg="#FFD700", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Contact", width=15, command=self.delete_contact, bg="#FF6347", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Search Contact", width=15, command=self.search_contact, bg="#98FB98", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=3, pady=5)

        # Treeview
        self.tree = ttk.Treeview(root, columns=("Name", "Phone", "Email", "Address"), show="headings", height=8)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_contacts()

    def add_contact(self):
        name = self.entries["name"].get().strip()
        phone = self.entries["phone"].get().strip()
        email = self.entries["email"].get().strip()
        address = self.entries["address"].get().strip()

        if name and phone:
            self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                                (name, phone, email, address))
            self.conn.commit()
            self.load_contacts()
            self.clear_entries()
        else:
            messagebox.showwarning("Warning", "Name and Phone are required!")

    def load_contacts(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM contacts")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, iid=row[0], values=row[1:])

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            for idx, key in enumerate(["name", "phone", "email", "address"]):
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, values[idx])

    def update_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a contact to update.")
            return
        contact_id = selected[0]
        name = self.entries["name"].get().strip()
        phone = self.entries["phone"].get().strip()
        email = self.entries["email"].get().strip()
        address = self.entries["address"].get().strip()

        if name and phone:
            self.cursor.execute("""
                UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?
            """, (name, phone, email, address, contact_id))
            self.conn.commit()
            self.load_contacts()
            self.clear_entries()
        else:
            messagebox.showwarning("Warning", "Name and Phone are required!")

    def delete_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a contact to delete.")
            return
        contact_id = selected[0]
        self.cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
        self.conn.commit()
        self.load_contacts()
        self.clear_entries()

    def search_contact(self):
        name = self.entries["name"].get().strip()
        phone = self.entries["phone"].get().strip()

        query = "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?"
        self.tree.delete(*self.tree.get_children())
        for row in self.cursor.execute(query, (f"%{name}%", f"%{phone}%")):
            self.tree.insert("", tk.END, iid=row[0], values=row[1:])

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBook(root)
    root.mainloop()
