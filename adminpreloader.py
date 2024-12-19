import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import bcrypt

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['student_management']
users_collection = db['users']

class AdminPreloadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin User Preloader")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Admin User Preloader", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="User ID (Numeric):").pack(pady=5)
        self.user_id_entry = tk.Entry(self)
        self.user_id_entry.pack(pady=5)

        tk.Label(self, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.pack(pady=5)

        tk.Label(self, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(self)
        self.email_entry.pack(pady=5)

        self.preload_button = tk.Button(self, text="Preload Admin User", command=self.preload_admin_user)
        self.preload_button.pack(pady=20)

    def preload_admin_user(self):
        user_id = self.user_id_entry.get()
        name = self.name_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        # Validate inputs
        if not user_id.isdigit() or not name or not password or not email:
            messagebox.showerror("Error", "All fields are required and User ID must be numeric.")
            return

        user_id = int(user_id)

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Prepare admin user data
        admin_user = {
            "user_id": user_id,
            "name": name,
            "password": hashed_password,
            "role": "admin",
            "email": email
        }

        # Insert the admin user if it doesn't exist
        if users_collection.find_one({"user_id": user_id}):
            messagebox.showerror("Error", "User ID already exists.")
        else:
            users_collection.insert_one(admin_user)
            messagebox.showinfo("Success", "Admin user created successfully!")
            self.clear_fields()

    def clear_fields(self):
        self.user_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

if __name__ == "__main__":
    app = AdminPreloadApp()
    app.mainloop()
