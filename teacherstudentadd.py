import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu
from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['student_management']
users_collection = db['users']
teachers_collection = db['teachers']
students_collection = db['students']
activity_log_collection = db['activity_log']

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin and Teacher Management System")
        self.geometry("400x300")
        self.main_menu()

    def main_menu(self):
        self.clear_window()

        tk.Label(self, text="Login as:", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Admin", command=self.admin_login).pack(pady=20)
        tk.Button(self, text="Teacher", command=self.teacher_login).pack(pady=20)

    def admin_login(self):
        self.clear_window()

        tk.Label(self, text="Admin Login", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="User ID:").pack(pady=5)
        self.admin_id_entry = tk.Entry(self)
        self.admin_id_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.admin_password_entry = tk.Entry(self, show='*')
        self.admin_password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.verify_admin).pack(pady=20)

    def verify_admin(self):
        user_id = self.admin_id_entry.get()
        password = self.admin_password_entry.get()

        admin_user = users_collection.find_one({"user_id": int(user_id), "role": "admin"})

        if admin_user and bcrypt.checkpw(password.encode('utf-8'), admin_user["password"].encode('utf-8')):
            messagebox.showinfo("Success", "Admin Login Successful!")
            self.admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Admin Credentials")

    def admin_dashboard(self):
        self.clear_window()

        tk.Label(self, text="Admin Dashboard", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Add Teacher", command=self.teacher_form).pack(pady=20)
        tk.Button(self, text="Logout", command=self.main_menu).pack(pady=20)

    def teacher_login(self):
        self.clear_window()

        tk.Label(self, text="Teacher Login", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="User ID:").pack(pady=5)
        self.teacher_id_entry = tk.Entry(self)
        self.teacher_id_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.teacher_password_entry = tk.Entry(self, show='*')
        self.teacher_password_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.verify_teacher).pack(pady=20)

    def verify_teacher(self):
        user_id = self.teacher_id_entry.get()
        password = self.teacher_password_entry.get()

        teacher_user = users_collection.find_one({"user_id": int(user_id), "role": "teacher"})

        if teacher_user and bcrypt.checkpw(password.encode('utf-8'), teacher_user["password"].encode('utf-8')):
            messagebox.showinfo("Success", "Teacher Login Successful!")
            self.teacher_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Teacher Credentials")

    def teacher_dashboard(self):
        self.clear_window()

        tk.Label(self, text="Teacher Dashboard", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Add Student", command=self.student_form).pack(pady=20)
        tk.Button(self, text="Logout", command=self.main_menu).pack(pady=20)

    def teacher_form(self):
        self.clear_window()

        tk.Label(self, text="Add Teacher", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="User ID:").pack(pady=5)
        self.new_teacher_id_entry = tk.Entry(self)
        self.new_teacher_id_entry.pack(pady=5)

        tk.Label(self, text="Name:").pack(pady=5)
        self.new_teacher_name_entry = tk.Entry(self)
        self.new_teacher_name_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.new_teacher_password_entry = tk.Entry(self, show='*')
        self.new_teacher_password_entry.pack(pady=5)

        tk.Label(self, text="Email:").pack(pady=5)
        self.new_teacher_email_entry = tk.Entry(self)
        self.new_teacher_email_entry.pack(pady=5)

        tk.Label(self, text="Department:").pack(pady=5)
        self.department_var = StringVar(self)
        self.department_var.set("Select Department")  # Default value
        department_dropdown = OptionMenu(self, self.department_var, "CSE", "ECE", "IT")
        department_dropdown.pack(pady=5)

        tk.Button(self, text="Add Teacher", command=self.add_teacher).pack(pady=20)
        tk.Button(self, text="Logout", command=self.main_menu).pack(pady=20)

    def add_teacher(self):
        user_id = self.new_teacher_id_entry.get()
        name = self.new_teacher_name_entry.get()
        password = self.new_teacher_password_entry.get()
        email = self.new_teacher_email_entry.get()
        department = self.department_var.get()

        if not (user_id and name and password and email and department != "Select Department"):
            messagebox.showerror("Error", "All fields are required.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            # Insert into users collection
            users_collection.insert_one({
                "user_id": int(user_id),
                "name": name,
                "password": hashed_password,
                "role": "teacher",
                "email": email
            })

            # Insert into teachers collection
            teachers_collection.insert_one({
                "user_id": int(user_id),
                "name": name,
                "department": department,
            })

            # Log the activity
            self.log_activity(user_id, name, "Added new teacher")

            messagebox.showinfo("Success", f"Teacher {name} added successfully!")
            self.teacher_form()  # Clear form for adding another teacher
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def student_form(self):
        self.clear_window()

        tk.Label(self, text="Add Student", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="User ID:").pack(pady=5)
        self.new_student_id_entry = tk.Entry(self)
        self.new_student_id_entry.pack(pady=5)

        tk.Label(self, text="Name:").pack(pady=5)
        self.new_student_name_entry = tk.Entry(self)
        self.new_student_name_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.new_student_password_entry = tk.Entry(self, show='*')
        self.new_student_password_entry.pack(pady=5)

        tk.Label(self, text="Email:").pack(pady=5)
        self.new_student_email_entry = tk.Entry(self)
        self.new_student_email_entry.pack(pady=5)

        tk.Label(self, text="Department:").pack(pady=5)
        self.department_var = StringVar(self)
        self.department_var.set("Select Department")  # Default value
        department_dropdown = OptionMenu(self, self.department_var, "CSE", "ECE", "IT")
        department_dropdown.pack(pady=5)

        tk.Button(self, text="Add Student", command=self.add_student).pack(pady=20)
        tk.Button(self, text="Logout", command=self.main_menu).pack(pady=20)

    def add_student(self):
        user_id = self.new_student_id_entry.get()
        name = self.new_student_name_entry.get()
        password = self.new_student_password_entry.get()
        email = self.new_student_email_entry.get()
        department = self.department_var.get()

        if not (user_id and name and password and email and department != "Select Department"):
            messagebox.showerror("Error", "All fields are required.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            # Insert into users collection
            users_collection.insert_one({
                "user_id": int(user_id),
                "name": name,
                "password": hashed_password,
                "role": "student",
                "email": email
            })

            # Insert into students collection
            students_collection.insert_one({
                "user_id": int(user_id),
                "name": name,
                "department": department,
            })

            # Create or update the corresponding department collection
            dept_collection = db[department]  # e.g., CSE, ECE
            student_doc = {
                "user_id": int(user_id),
                "name": name,
                "subjects": {
                    "subject1": None,
                    "subject2": None,
                    "subject3": None,
                    "subject4": None,
                    "subject5": None
                }
            }

            # Check if a document for the student already exists
            existing_student = dept_collection.find_one({"user_id": int(user_id)})
            if existing_student:
                # Update the existing student's document
                dept_collection.update_one(
                    {"user_id": int(user_id)},
                    {"$set": student_doc}
                )
            else:
                # Insert a new document for the student
                dept_collection.insert_one(student_doc)

            # Log the activity
            self.log_activity(user_id, name, "Added new student")

            messagebox.showinfo("Success", f"Student {name} added successfully!")
            self.student_form()  # Clear form for adding another student
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def log_activity(self, user_id, name, action):
        """Log the activity into the activity_log collection."""
        try:
            activity_log_collection.insert_one({
                "user_id": int(user_id),
                "name": name,
                "action": action,
                "timestamp": datetime.now()
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to log activity: {e}")

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
