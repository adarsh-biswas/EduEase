# EduEase: A MongoDB-Powered Student Management System

## Overview
EduEase is an end-to-end student management application designed to streamline student registration, department-specific data organization, and grade management. Built using Python, Tkinter, and MongoDB, this application provides role-based access for Admins, Teachers, and Students.

---

## Features

### Admin Features:
- Manage teacher and student data.
- Role-based access control.
- Secure authentication using bcrypt.

### Teacher Features:
- Add and manage student grades.
- View students in their assigned department.

### Student Features:
- View personal information and grades.
- Access department-specific data.

---

## Technology Stack
- **Programming Language:** Python
- **Database:** MongoDB
- **Frontend:** Tkinter (Python GUI library)
- **Libraries Used:**
  - `tkinter` for GUI.
  - `pymongo` for MongoDB integration.
  - `bcrypt` for secure password hashing.

---

## File Structure
1. **`adminpreloader.py`:**
   - Handles admin authentication and preloading functionalities.
   - Connects to the `users` collection in MongoDB.

2. **`main.py`:**
   - Entry point of the application.
   - Provides role-based navigation (Admin, Teacher, Student).
   - Integrates with MongoDB to fetch and store data.

3. **`teacherstudentadd.py`:**
   - Adds new teachers and students to the database.
   - Interacts with collections like `users`, `teachers`, and `students`.

---

## Installation and Setup

### Prerequisites
- Python 3.8+
- MongoDB installed and running locally or on a server.
- Required Python packages (install using `pip`):
  ```bash
  pip install pymongo bcrypt
  ```

### Steps to Run the Application
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd EduEase
   ```
2. Ensure MongoDB is running on your system.
3. Run the application:
   ```bash
   python main.py
   ```

---

## Database Schema

### Collections:
1. **`users`**:
   - Fields:
     - `username` (string): Unique username.
     - `password` (string): Hashed password.
     - `role` (string): Role of the user (Admin, Teacher, Student).

2. **`teachers`**:
   - Fields:
     - `teacher_id` (string): Unique teacher identifier.
     - `department` (string): Assigned department.

3. **`students`**:
   - Fields:
     - `roll_number` (string): Unique roll number.
     - `department` (string): Assigned department.
     - `grades` (array): List of grades.

---

## Future Enhancements
- Add graph-based analytics for grade trends.
- Implement email notifications for users.
- Introduce a web-based interface.

---

## Contributors
- **Adarsh**: Developer.
