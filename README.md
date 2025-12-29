# 📚 Library Management System

A comprehensive desktop application for managing university library operations with advanced database features including stored procedures, triggers, and dynamic query building.

## 🎯 Project Overview

This Library Management System is a full-featured desktop application built with Python and MySQL. It provides a complete solution for library operations including member management, book inventory control, loan tracking, automatic penalty calculation, and comprehensive reporting capabilities.

**Developed as a Database Management Systems (DBMS) Final Project**

## ✨ Key Features

### Core Functionality
- 👥 **Member Management** - Complete CRUD operations for library members
- 📖 **Book Inventory** - Track books with categories, stock levels, and availability
- 🔄 **Loan Operations** - Issue and return books with automatic date calculations
- 💰 **Automated Penalties** - Calculate late fees automatically (5 TL per day)
- 📊 **Comprehensive Reports** - Multiple report types with export capabilities
- 🔍 **Dynamic Query Builder** - Build complex queries with multiple filters

### Database Features
- **3 Stored Procedures** - Business logic encapsulation
  - `sp_YeniOduncVer` - Issue new loan with validations
  - `sp_KitapTeslimAl` - Return book with penalty calculation
  - `sp_UyeOzetRapor` - Member summary report
- **4 Database Triggers** - Automated operations
  - Stock management triggers
  - Penalty calculation triggers
  - Operation logging triggers
  - Member deletion protection
- **Transaction Logging** - All operations logged in JSON format

### Reports & Analytics
- 📅 Loans by date range
- ⏰ Overdue books report
- 📈 Most borrowed books statistics
- 👤 Member activity reports
- 📊 Statistical dashboard

## 🛠️ Technology Stack

| Category | Technology |
|----------|-----------|
| **Language** | Python 3.13 |
| **GUI Framework** | PyQt5 |
| **Database** | MySQL 8.0 |
| **Charting** | Matplotlib |
| **PDF Export** | ReportLab |
| **Excel Export** | OpenPyXL |

## 📋 Prerequisites

- Python 3.13 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Git

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ahmetkahranam/dbms-final-project.git
cd dbms-final-project
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database

Create a new database:
```sql
CREATE DATABASE kutuphane_db CHARACTER SET utf8mb4 COLLATE utf8mb4_turkish_ci;
```

Run SQL scripts in order:
```bash
# Windows (using MySQL command line)
mysql -u root -p kutuphane_db < database/schema.sql
mysql -u root -p kutuphane_db < database/stored_procedures.sql
mysql -u root -p kutuphane_db < database/triggers.sql
mysql -u root -p kutuphane_db < database/sample_data.sql
```

Or use MySQL Workbench to execute each script file.

### 5. Configure Database Connection

Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kutuphane_db
DB_USER=root
DB_PASSWORD=your_mysql_password
```

### 6. Run the Application
```bash
python main.py
```

## 🔐 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Staff | `gorevli1` | `123456` |

## 📁 Project Structure

```
dbms-final-project/
├── database/                    # Database SQL scripts
│   ├── schema.sql              # Table definitions
│   ├── stored_procedures.sql   # Stored procedures
│   ├── triggers.sql            # Database triggers
│   └── sample_data.sql         # Sample data for testing
├── src/
│   ├── config/                 # Configuration management
│   │   └── database.py         # Database connection
│   ├── models/                 # Data models
│   │   ├── book.py
│   │   ├── member.py
│   │   ├── loan.py
│   │   ├── penalty.py
│   │   └── user.py
│   ├── database/               # Database operations
│   │   └── db_manager.py       # Database manager class
│   ├── ui/                     # User interface
│   │   ├── login_window.py
│   │   ├── dashboard_window.py
│   │   ├── book_management_window.py
│   │   ├── member_management_window.py
│   │   ├── category_window.py
│   │   ├── loan_window.py
│   │   ├── penalty_window.py
│   │   ├── dynamic_query_window.py
│   │   ├── reports_window.py
│   │   └── reports/            # Report windows
│   ├── utils/                  # Utility functions
│   │   ├── validators.py       # Input validation
│   │   ├── helpers.py          # Helper functions
│   │   └── toast_notification.py
│   └── resources/              # UI resources
│       ├── icons/
│       └── styles/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
└── README.md
```

## 💾 Database Schema

### Main Tables
- **KULLANICI** - System users (Admin/Staff)
- **UYE** - Library members
- **KATEGORI** - Book categories
- **KITAP** - Books inventory
- **ODUNC** - Loan records
- **CEZA** - Penalties/fines
- **LOG_ISLEM** - Operation logs

## 🎨 Screenshots

### Login Screen
Professional login interface with role-based authentication.

### Dashboard
Overview of library statistics and quick access to all modules.

### Book Management
Complete book inventory management with category filtering.

### Loan Operations
Issue and return books with automatic validation and penalty calculation.

### Dynamic Query Builder
Build complex queries with multiple filters for books and members.

### Reports
Comprehensive reporting with export to Excel and PDF.

## 🔧 Database Features

### Stored Procedures
1. **sp_YeniOduncVer** - Issue new loan
   - Validates member loan limit (max 5 active loans)
   - Checks book availability
   - Updates stock automatically
   - Calculates due date (15 days)

2. **sp_KitapTeslimAl** - Process book return
   - Updates return date
   - Calculates overdue penalty
   - Updates member balance
   - Restores stock

3. **sp_UyeOzetRapor** - Member summary
   - Total books borrowed
   - Active loans count
   - Penalty statistics

### Database Triggers
1. **TR_ODUNC_INSERT** - After loan insert
2. **TR_ODUNC_UPDATE_TESLIM** - After return update
3. **TR_CEZA_INSERT** - After penalty insert
4. **TR_UYE_DELETE_BLOCK** - Prevent member deletion

## 🧪 Testing

Sample data is included in `database/sample_data.sql`:
- 2 system users (admin, staff)
- 10 library members
- 5 categories
- 15 books
- Sample loan records

## 🤝 Contributing

This project was developed as an educational project for Database Management Systems course. Contributions and suggestions are welcome!

## 📝 License

This project is developed for educational purposes as part of a Database Management Systems course.

## 👨‍💻 Author

**Ahmet Kahraman**
- GitHub: [@ahmetkahranam](https://github.com/ahmetkahranam)

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note:** This is an academic project demonstrating database design principles, stored procedures, triggers, and GUI development with Python.
