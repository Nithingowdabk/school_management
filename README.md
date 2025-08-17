# School Management System

A comprehensive web-based School Management System built with Python Flask backend and modern web technologies. This system provides efficient management of students, fee tracking, automated email reminders, and AI-powered teacher performance analysis.

## 🚀 Features

### Core Functionality
- **Student Management**: Add, view, and delete student records with parent information
- **Fee Management**: Track pending fees, automated reminder system with round-based notifications
- **Teacher Performance Analysis**: AI-powered evaluation with PDF report generation
- **Email Notifications**: Automated fee reminder emails to parents
- **Database Integration**: MySQL database with comprehensive data management

### Advanced Features
- **AI Teacher Performance**: Intelligent analysis of teacher metrics including feedback, attendance, and results
- **PDF Report Generation**: Professional landscape-oriented reports using ReportLab
- **Email Automation**: SMTP-based email system for parent notifications
- **Reminder Scheduling**: Smart reminder system that sends notifications in rounds
- **RESTful API**: Complete API endpoints for all system operations

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**: Core programming language
- **Flask**: Web framework for API development
- **MySQL**: Database management system
- **ReportLab**: PDF generation library
- **SMTP**: Email notification system

### Frontend
- **HTML5/CSS3**: Modern web interface
- **JavaScript**: Interactive user experience
- **React**: Component-based UI development

### Libraries & Dependencies
- `flask`: Web framework
- `mysql-connector-python`: MySQL database connectivity
- `reportlab`: PDF generation
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `flask-cors`: Cross-Origin Resource Sharing

## 📋 Prerequisites

Before running this project, make sure you have:

- Python 3.12 or higher
- MySQL Server installed and running
- Gmail account for email notifications (or SMTP server)
- pip package manager

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/nithingowdabk/school_management.git
cd school_management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
1. Install MySQL and create a database named `school_management`
2. Create the required tables:

```sql
-- Students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_class VARCHAR(50),
    parent_name VARCHAR(100) NOT NULL,
    parent_email VARCHAR(100) UNIQUE NOT NULL,
    parent_phone VARCHAR(20)
);

-- Fees table
CREATE TABLE fees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    parent_name VARCHAR(100) NOT NULL,
    parent_email VARCHAR(100) NOT NULL,
    amount_due DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Pending',
    reminder_count INT DEFAULT 0
);

-- Teacher Performance table
CREATE TABLE teacher_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(100) NOT NULL,
    feedback_score DECIMAL(5,2),
    attendance_percentage DECIMAL(5,2),
    result_percentage DECIMAL(5,2),
    activity_score DECIMAL(5,2),
    final_score DECIMAL(5,2),
    rating VARCHAR(20),
    ai_suggestion TEXT
);
```

### 4. Configuration
Update the configuration in `config/settings.py`:

```python
# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "your_mysql_username",
    "password": "your_mysql_password",
    "database": "school_management"
}

# Email Configuration (Gmail example)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "port": 587,
    "EMAIL_ADDRESS": "your_email@gmail.com",
    "EMAIL_PASSWORD": "your_app_password"  # Use App Password for Gmail
}
```

## 🚀 Usage

### Running the Application
```bash
python app.py
```
The application will start on `http://localhost:5000`

### Accessing MySQL Database
```bash
mysql -h localhost -u root -p
USE school_management;
SHOW TABLES;
```

## 📖 API Endpoints

### Student Management
- `GET /api/students` - Retrieve all students
- `POST /api/add-student` - Add new student
- `DELETE /api/delete-student/<id>` - Delete student

### Fee Management
- `GET /api/pending-fees` - Get all pending fees
- `POST /api/send-all-reminders` - Send fee reminder emails
- `DELETE /api/mark-fee-paid/<id>` - Mark fee as paid

### Teacher Performance
- `GET /api/teacher-performance` - Generate teacher performance report

### System
- `GET /api/check-db-connection` - Check database connectivity

## 🔧 Project Structure

```
school_management/
├── app.py                     # Main Flask application
├── main.py                    # Alternative entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── TeacherPerformanceAI.py   # AI performance analysis
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration settings
├── models/
│   └── fee_record.py         # Fee record model
├── services/
│   ├── fee_tracking.py       # Fee tracking service
│   ├── notification.py       # Email notification service
│   └── reminder_scheduler.py # Reminder scheduling
├── utils/
│   └── helper.py            # Utility functions
├── public/                  # Frontend files
│   ├── index.html
│   ├── add-student.html
│   ├── fees.html
│   ├── teacher-performance.html
│   ├── student-details.html
│   ├── styles.css
│   └── scripts.js
└── build/                   # Production build files
```

## ✨ Key Features Explained

### 1. Smart Fee Reminder System
The system implements a round-based reminder strategy:
- Sends reminders only to those with the minimum reminder count
- Prevents spam by organizing reminders in rounds
- Tracks reminder history for each fee record

### 2. AI Teacher Performance Analysis
- Evaluates multiple metrics: feedback scores, attendance, results, activities
- Generates AI-powered suggestions for improvement
- Creates professional PDF reports with landscape orientation

### 3. Email Automation
- SMTP integration for automated email sending
- Professional email templates for fee reminders
- Error handling and logging for email delivery

## 🔒 Security Considerations

- Store sensitive configuration in environment variables
- Use app passwords for Gmail integration
- Implement proper input validation
- Use parameterized queries to prevent SQL injection
- Consider implementing authentication and authorization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Nithin Gowda BK**
- GitHub: [@nithingowdabk](https://github.com/nithingowdabk)
- Email: nithinkempegowda.levontechno@gmail.com

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- ReportLab for PDF generation capabilities
- MySQL for robust database management
- Contributors and testers

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the existing issues on GitHub
2. Create a new issue with detailed description
3. Contact the author via email

---

⭐ **Star this repository if you find it helpful!**

## 🌐 Live Demo

Check out the live repository: [https://github.com/Nithingowdabk/school_management](https://github.com/Nithingowdabk/school_management)

## 📊 Project Screenshots

*Add screenshots of your application here to showcase the user interface*

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL server is running
   - Verify database credentials in `config/settings.py`
   - Check if the database `school_management` exists

2. **Email Not Sending**
   - Verify Gmail App Password is correct
   - Check SMTP server settings
   - Ensure "Less secure app access" is enabled (if not using App Password)

3. **Module Not Found Error**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct project directory

### Getting Help

If you encounter issues not covered here, please create an issue on GitHub with:
- Error message details
- Your system configuration
- Steps to reproduce the problem
