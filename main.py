import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk  # Import ttk for Combobox
from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['student_management']
users_collection = db['users']
students_collection = db['students']
teachers_collection = db['teachers']
activity_log_collection = db['activity_log']
departments_collection = {
    "CSE": db['CSE'],
    "ECE": db['ECE'],
    "IT": db['IT'],
}

# Add subjects to department collections and create index for average_score
for dept in departments_collection.values():
    if dept.count_documents({}) == 0:  # Only add subjects if collection is empty
        subjects = ["subject1", "subject2", "subject3", "subject4", "subject5"]
        dept.insert_one({"department": dept.name, "subjects": subjects})

    # Create descending index on average_score for each department collection
    dept.create_index([("average_score", -1)])


class StudentManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("400x300")
        self.login_page()

    def login_page(self):
        self.clear_window()

        tk.Label(self, text="Login", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Admin Login", command=lambda: self.login("admin")).pack(pady=5)
        tk.Button(self, text="Teacher Login", command=lambda: self.login("teacher")).pack(pady=5)
        tk.Button(self, text="Student Login", command=lambda: self.login("student")).pack(pady=5)

    def login(self, role):
        user_id = simpledialog.askinteger("User ID", "Enter User ID (Numeric):")
        password = simpledialog.askstring("Password", "Enter Password:", show='*')

        if user_id is None or password is None:
            messagebox.showerror("Error", "User ID and Password are required.")
            return

        user = users_collection.find_one({"user_id": user_id})
        if role == "teacher":
            teacher = teachers_collection.find_one({"user_id": user_id})
            if user and teacher and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')) and user[
                "role"] == role:
                messagebox.showinfo("Login", f"{role.capitalize()} Login Successful!")
                self.main_page(role)
            else:
                messagebox.showerror("Error", "Invalid Credentials")
        else:
            if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')) and user[
                "role"] == role:
                messagebox.showinfo("Login", f"{role.capitalize()} Login Successful!")
                self.main_page(role)
            else:
                messagebox.showerror("Error", "Invalid Credentials")

    def main_page(self, role):
        self.clear_window()

        tk.Label(self, text=f"{role.capitalize()} Dashboard", font=("Arial", 16)).pack(pady=10)

        # Common Logout Button
        tk.Button(self, text="Logout", command=self.login_page).pack(pady=5)

        if role == "admin":
            tk.Button(self, text="View Teachers List", command=self.view_teachers).pack(pady=5)
            tk.Button(self, text="Show Activity", command=self.show_activity).pack(pady=5)

        elif role == "teacher":
            tk.Button(self, text="View Students", command=self.view_students).pack(pady=5)
            tk.Button(self, text="Add Grades", command=self.add_grades).pack(pady=5)
            tk.Button(self, text="Top 3 Toppers", command=self.top_toppers).pack(pady=5)
            tk.Button(self, text="Average Marks of Subjects", command=self.average_marks_subject).pack(pady=5)
            tk.Button(self, text="Distinction Students", command=self.distinction_students).pack(pady=5)
            tk.Button(self, text="Failed Students", command=self.failed_students).pack(pady=5)

        elif role == "student":
            tk.Button(self, text="View Details", command=self.view_student_details).pack(pady=5)
            tk.Button(self, text="View Marks", command=self.view_student_marks).pack(pady=5)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def add_grades(self):
        student_id = simpledialog.askinteger("Student ID", "Enter Student User ID (Numeric):")

        if student_id is None:
            messagebox.showerror("Error", "Student ID is required.")
            return

        student = students_collection.find_one({"user_id": student_id})

        if not student:
            messagebox.showerror("Error", "Student not found.")
            return

        grades = {}
        subjects = ["subject1", "subject2", "subject3", "subject4", "subject5"]

        # Get grades for each subject
        for subject in subjects:
            grade = simpledialog.askfloat("Grade Entry", f"Enter grade for {subject}:")
            if grade is not None:
                grades[subject] = grade

        department = student['department']

        # Calculate the average score of all subjects
        total_score = sum(grades.values())
        average_score = total_score / len(subjects)

        # Update student grades and store the average score
        update_result = departments_collection[department].update_one(
            {"user_id": student_id},
            {
                "$set": {
                    **{f"subjects.{subject}": grades[subject] for subject in subjects},  # Enclosed in {}
                    "average_score": average_score  # Store the calculated average score
                }
            }
        )

        if update_result.modified_count == 0:
            messagebox.showinfo("Update Grades", "No grades updated, please check if the student exists.")
        else:
            self.log_activity(student_id, student['name'], "Grades Updated")
            messagebox.showinfo("Success",
                                f"Grades for Student ID {student_id} updated successfully! Average Score: {average_score}")

    def view_students(self):
        students = students_collection.find()
        student_list = "\n".join(
            [f"ID: {s['user_id']}, Name: {s['name']}, Department: {s['department']}" for s in students]
        )
        messagebox.showinfo("Students", student_list if student_list else "No students found.")

    def view_teachers(self):
        teachers = teachers_collection.find()
        teacher_list = "\n".join([f"{t['user_id']}: {t['name']} - {t['department']}" for t in teachers])
        messagebox.showinfo("Teachers", teacher_list if teacher_list else "No teachers found.")

    def view_student_details(self):
        user_id = simpledialog.askinteger("User ID", "Enter Your User ID:")
        student = students_collection.find_one({"user_id": user_id})

        if student:
            details = "\n".join([f"{key.capitalize()}: {value}" for key, value in student.items()])
            messagebox.showinfo("Student Details", details)
        else:
            messagebox.showerror("Error", "Student not found.")

    def view_student_marks(self):
        user_id = simpledialog.askinteger("User ID", "Enter Your User ID:")
        student = students_collection.find_one({"user_id": user_id})

        if student:
            department = student['department']
            marks = departments_collection[department].find_one({"user_id": user_id})
            if marks:
                student_grades = marks['subjects']
                student_marks = "\n".join(
                    [f"{subject}: {grade}" for subject, grade in student_grades.items() if grade is not None])
                messagebox.showinfo("Marks", student_marks if student_marks else "No marks found.")
            else:
                messagebox.showerror("Error", "Marks not found.")
        else:
            messagebox.showerror("Error", "Student not found.")

    def top_toppers(self):
        # Create a new window for selecting department
        department_window = tk.Toplevel(self)
        department_window.title("Select Department")

        tk.Label(department_window, text="Select Department:", font=("Arial", 12)).pack(pady=10)

        department_combobox = ttk.Combobox(department_window, values=list(departments_collection.keys()))
        department_combobox.pack(pady=5)
        department_combobox.set("Select a Department")  # Default text

        def submit_department():
            department = department_combobox.get()
            if department not in departments_collection:
                messagebox.showerror("Error", "Invalid Department.")
                return

            toppers = departments_collection[department].aggregate([
                {
                    "$project": {
                        "user_id": 1,
                        "name": 1,
                        "average_score": {
                            "$avg": [
                                {"$ifNull": ["$subjects.subject1", 0]},
                                {"$ifNull": ["$subjects.subject2", 0]},
                                {"$ifNull": ["$subjects.subject3", 0]},
                                {"$ifNull": ["$subjects.subject4", 0]},
                                {"$ifNull": ["$subjects.subject5", 0]},
                            ]
                        }
                    }
                },
                {"$sort": {"average_score": -1}},
                {"$limit": 3}
            ])

            toppers_list = "\n".join(
                [f"ID: {t['user_id']}, Name: {t['name']}, Average Score: {t['average_score']}" for t in toppers])
            messagebox.showinfo("Top 3 Toppers", toppers_list if toppers_list else "No toppers found.")

            department_window.destroy()

        tk.Button(department_window, text="Submit", command=submit_department).pack(pady=10)

    def average_marks_subject(self):
        department_window = tk.Toplevel(self)
        department_window.title("Select Department")

        tk.Label(department_window, text="Select Department:", font=("Arial", 12)).pack(pady=10)

        department_combobox = ttk.Combobox(department_window, values=list(departments_collection.keys()))
        department_combobox.pack(pady=5)
        department_combobox.set("Select a Department")

        def submit_department():
            department = department_combobox.get()
            if department not in departments_collection:
                messagebox.showerror("Error", "Invalid Department.")
                return

            result = departments_collection[department].aggregate([
                {"$project": {
                    "subjects": 1
                }},
                {"$group": {
                    "_id": None,
                    "subject1_avg": {"$avg": "$subjects.subject1"},
                    "subject2_avg": {"$avg": "$subjects.subject2"},
                    "subject3_avg": {"$avg": "$subjects.subject3"},
                    "subject4_avg": {"$avg": "$subjects.subject4"},
                    "subject5_avg": {"$avg": "$subjects.subject5"}
                }}
            ])

            average_marks = next(result, None)
            if average_marks:
                avg_marks_list = "\n".join([f"{subject}: {average_marks[subject + '_avg']:.2f}" for subject in
                                            ["subject1", "subject2", "subject3", "subject4", "subject5"]])
                messagebox.showinfo("Average Marks", avg_marks_list)
            else:
                messagebox.showinfo("Average Marks", "No marks found.")

            department_window.destroy()

        tk.Button(department_window, text="Submit", command=submit_department).pack(pady=10)

    def distinction_students(self):
        # Create a new window for selecting department
        department_window = tk.Toplevel(self)
        department_window.title("Select Department")

        tk.Label(department_window, text="Select Department:", font=("Arial", 12)).pack(pady=10)

        department_combobox = ttk.Combobox(department_window, values=list(departments_collection.keys()))
        department_combobox.pack(pady=5)
        department_combobox.set("Select a Department")  # Default text

        def submit_department():
            department = department_combobox.get()
            if department not in departments_collection:
                messagebox.showerror("Error", "Invalid Department.")
                return

            distinction_students = departments_collection[department].aggregate([
                {
                    "$match": {
                        "average_score": {"$gte": 7}
                    }
                },
                {
                    "$project": {
                        "user_id": 1,
                        "name": 1,
                        "average_score": 1
                    }
                }
            ])

            distinction_list = list(distinction_students)
            if distinction_list:
                result = "\n".join(
                    [f"ID: {s['user_id']}, Name: {s['name']}, Average Score: {s['average_score']}" for s in
                     distinction_list])
                messagebox.showinfo("Distinction Students", result)
            else:
                messagebox.showinfo("Distinction Students", "No distinction students found.")
            department_window.destroy()  # Close the window after getting results

        tk.Button(department_window, text="Submit", command=submit_department).pack(pady=10)

    def failed_students(self):
        # Create a new window for selecting department
        department_window = tk.Toplevel(self)
        department_window.title("Select Department")

        tk.Label(department_window, text="Select Department:", font=("Arial", 12)).pack(pady=10)

        department_combobox = ttk.Combobox(department_window, values=list(departments_collection.keys()))
        department_combobox.pack(pady=5)
        department_combobox.set("Select a Department")  # Default text

        def submit_department():
            department = department_combobox.get()
            if department not in departments_collection:
                messagebox.showerror("Error", "Invalid Department.")
                return

            failed_students = departments_collection[department].aggregate([
                {
                    "$match": {
                        "average_score": {"$lt": 5}
                    }
                },
                {
                    "$project": {
                        "user_id": 1,
                        "name": 1,
                        "average_score": 1
                    }
                }
            ])

            failed_list = list(failed_students)
            if failed_list:
                result = "\n".join(
                    [f"ID: {s['user_id']}, Name: {s['name']}, Average Score: {s['average_score']}" for s in
                     failed_list])
                messagebox.showinfo("Failed Students", result)
            else:
                messagebox.showinfo("Failed Students", "No failed students found.")
            department_window.destroy()  # Close the window after getting results

        tk.Button(department_window, text="Submit", command=submit_department).pack(pady=10)

    def log_activity(self, user_id, name, action):
        log_entry = {
            "user_id": user_id,
            "name": name,
            "action": action,
            "timestamp": datetime.now()
        }
        activity_log_collection.insert_one(log_entry)

    def show_activity(self):
        logs = activity_log_collection.find().sort("timestamp", -1)
        log_list = "\n".join(
            [f"User: {log.get('name', 'Unknown')} (ID: {log['user_id']}) - {log['action']} at {log['timestamp']}" for
             log in logs])
        messagebox.showinfo("Activity Log", log_list if log_list else "No activity recorded.")


if __name__ == "__main__":
    app = StudentManagementApp()
    app.mainloop()
