document.addEventListener("DOMContentLoaded", function () {
    // --- Teacher Performance --- //
    const tableBody = document.getElementById("teacher-performance-body");
    const fetchButton = document.getElementById("fetch-performance");
    const performanceResult = document.getElementById("performance-result");
    const performanceTable = document.querySelector("#teacher-performance table");
    const downloadContainer = document.getElementById("download-container");
    let teacherPerformanceVisible = false;

    fetchButton.addEventListener('click', () => {
        if (teacherPerformanceVisible) {
            // Hide elements if already visible
            performanceResult.textContent = "";
            tableBody.innerHTML = '';
            downloadContainer.innerHTML = '';
            performanceTable.style.display = 'none';
            teacherPerformanceVisible = false;
        } else {
            // Fetch and display data
            performanceResult.textContent = "Fetching data...";
            tableBody.innerHTML = '';
            downloadContainer.innerHTML = '';
            performanceTable.style.display = 'none';

            fetch("/api/teacher-performance")
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    performanceResult.textContent = data.message;
                    if (data && data.data && data.data.length > 0) {
                        performanceTable.style.display = 'table';
                        data.data.forEach(teacher => {
                            const row = document.createElement("tr");
                            row.innerHTML = `
                                <td>${teacher.name}</td>
                                <td>${teacher.feedback_score}</td>
                                <td>${teacher.attendance_percentage}</td>
                                <td>${teacher.result_percentage}</td>
                                <td>${teacher.activity_score}</td>
                                <td>${teacher.final_score}</td>
                                <td>${teacher.rating}</td>
                                <td>${teacher.ai_suggestion}</td>
                            `;
                            tableBody.appendChild(row);
                        });

                        if (data.pdf_download_link) {
                            const downloadLink = document.createElement('a');
                            downloadLink.href = data.pdf_download_link;
                            downloadLink.textContent = 'Download PDF Report';
                            downloadLink.setAttribute('download', 'teacher_performance.pdf');
                            downloadLink.style.display = 'block';
                            downloadLink.style.marginTop = '10px';
                            downloadContainer.appendChild(downloadLink);
                        }
                        teacherPerformanceVisible = true; // Mark as visible
                    } else if (data && data.data && data.data.length === 0) {
                        performanceResult.textContent = "No teacher performance data found.";
                        performanceTable.style.display = 'none';
                        teacherPerformanceVisible = false; // Still hidden
                    } else {
                        performanceResult.textContent = data.message || "Received unexpected data format.";
                        performanceTable.style.display = 'none';
                        teacherPerformanceVisible = false; // Still hidden
                    }
                })
                .catch(error => {
                    console.error("Error fetching teacher performance data:", error);
                    performanceResult.textContent = `Error fetching data: ${error.message}`;
                    performanceTable.style.display = 'none';
                    teacherPerformanceVisible = false; // Still hidden
                });
        }
    });

    // --- Fees Reminder Logic --- //
    const fetchPendingButton = document.getElementById('fetch-pending-button');
    const pendingFeesStatus = document.getElementById('pending-fees-status');
    const pendingFeesDisplayTable = document.getElementById('pending-fees-display-table');
    const pendingFeesDisplayBody = document.getElementById('pending-fees-display-body');
    const sendAllRemindersButton = document.getElementById('send-all-reminders-button');
    const reminderResult = document.getElementById('reminder-result');
    const sentRemindersTable = document.getElementById('sent-reminders-table');
    const sentRemindersBody = document.getElementById('sent-reminders-body');
    let pendingFeesVisible = false;

    fetchPendingButton.addEventListener('click', () => {
        if (pendingFeesVisible) {
            // Hide elements
            pendingFeesStatus.textContent = "";
            pendingFeesDisplayBody.innerHTML = '';
            pendingFeesDisplayTable.style.display = 'none';
            sendAllRemindersButton.style.display = 'none';
            sentRemindersTable.style.display = 'none';
            reminderResult.textContent = '';
            pendingFeesVisible = false;
        } else {
            // Fetch and display pending fees
            pendingFeesStatus.textContent = "Fetching pending fees...";
            pendingFeesDisplayBody.innerHTML = '';
            pendingFeesDisplayTable.style.display = 'none';
            sendAllRemindersButton.style.display = 'none';
            sentRemindersTable.style.display = 'none';
            reminderResult.textContent = '';

            fetch('/api/pending-fees')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (Array.isArray(data) && data.length > 0) {
                        pendingFeesStatus.textContent = `Found ${data.length} pending fee records. Click 'Send All Reminders' to notify parents.`;
                        pendingFeesDisplayTable.style.display = 'table';
                        sendAllRemindersButton.style.display = 'block';
                        data.forEach(record => {
                            const row = document.createElement("tr");
                            // Store fee_id on the row for easy access during deletion
                            row.setAttribute('data-fee-id', record.fee_id);
                            row.innerHTML = `
                                <td>${record.student_name}</td>
                                <td>${record.parent_name}</td>
                                <td>${record.amount_due}</td>
                                <td>${record.due_date}</td>
                                <td>${record.parent_email}</td>
                                <td>${record.payment_status}</td>
                                <td>
                                    <button class="mark-paid-btn" data-fee-id="${record.fee_id}">Mark as Paid</button>
                                </td>
                            `;
                            pendingFeesDisplayBody.appendChild(row);
                        });
                        pendingFeesVisible = true; // Mark as visible
                    } else if (Array.isArray(data) && data.length === 0) {
                        pendingFeesStatus.textContent = "No pending fee records found.";
                        pendingFeesDisplayTable.style.display = 'none';
                        sendAllRemindersButton.style.display = 'none';
                        pendingFeesVisible = false;
                    } else {
                        const errorMessage = data.error ? `${data.error}: ${data.details}` : "Received unexpected data format.";
                        pendingFeesStatus.textContent = `Error: ${errorMessage}`;
                        pendingFeesDisplayTable.style.display = 'none';
                        sendAllRemindersButton.style.display = 'none';
                        pendingFeesVisible = false;
                    }
                })
                .catch(error => {
                    console.error("Error fetching pending fees:", error);
                    pendingFeesStatus.textContent = `Error fetching pending fees: ${error.message}`;
                    pendingFeesDisplayTable.style.display = 'none';
                    sendAllRemindersButton.style.display = 'none';
                    pendingFeesVisible = false;
                });
        }
    });

    // Add event listener for the "Mark as Paid" buttons using event delegation
    pendingFeesDisplayBody.addEventListener('click', (event) => {
        if (event.target.classList.contains('mark-paid-btn')) {
            const button = event.target;
            const feeId = button.dataset.feeId;
            const row = button.closest('tr');
            const studentName = row.cells[0].textContent; // Get student name from the row

            if (confirm(`Are you sure you want to mark the fee for ${studentName} (ID: ${feeId}) as paid? This will remove the record.`)) {
                pendingFeesStatus.textContent = `Marking fee ${feeId} as paid...`;
                pendingFeesStatus.style.color = 'black';

                fetch(`/api/mark-fee-paid/${feeId}`, {
                    method: 'DELETE',
                })
                .then(response => {
                    const status = response.status;
                    // Try to parse JSON, but handle cases where the body might be empty or not JSON
                    return response.text().then(text => {
                        try {
                            const data = JSON.parse(text);
                            return { status, data };
                        } catch (e) {
                            // If parsing fails, use the text directly or a default message
                            return { status, data: { message: text || `Request completed with status ${status}` } };
                        }
                    });
                })
                .then(({ status, data }) => {
                    if (status === 200) {
                        pendingFeesStatus.textContent = data.message || `Fee ${feeId} marked as paid successfully.`;
                        pendingFeesStatus.style.color = 'green';
                        row.remove(); // Remove the row from the table

                        // Update count and visibility if table becomes empty
                        const remainingRows = pendingFeesDisplayBody.children.length;
                        if (remainingRows === 0) {
                            pendingFeesDisplayTable.style.display = 'none';
                            sendAllRemindersButton.style.display = 'none';
                            pendingFeesStatus.textContent = "No pending fee records remaining.";
                            pendingFeesVisible = false;
                        } else {
                            pendingFeesStatus.textContent = `Found ${remainingRows} pending fee records.`;
                        }
                    } else {
                        // Throw error for non-200 status codes
                        throw new Error(data.details || data.error || data.message || `Failed to mark fee as paid (Status: ${status})`);
                    }
                })
                .catch(error => {
                    console.error('Error marking fee as paid:', error);
                    pendingFeesStatus.textContent = `Error: ${error.message}`;
                    pendingFeesStatus.style.color = 'red';
                });
            }
        }
    });

    // Event listener for sending all reminders (no toggle needed here, it's an action)
    sendAllRemindersButton.addEventListener('click', () => {
        reminderResult.textContent = "Processing and sending reminders...";
        sentRemindersBody.innerHTML = ''; // Clear previous sent details
        sentRemindersTable.style.display = 'none'; // Hide sent table initially

        fetch('/api/send-all-reminders', { method: 'POST' }) // Use the endpoint that sends emails
            .then(response => response.json())
            .then(data => {
                reminderResult.textContent = data.message;

                // Populate the sent reminders table
                if (data.reminders_sent_details && data.reminders_sent_details.length > 0) {
                    sentRemindersTable.style.display = 'table'; // Show sent table
                    data.reminders_sent_details.forEach(reminder => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${reminder.student_name}</td>
                            <td>${reminder.parent_email}</td>
                            <td>${reminder.due_date}</td>
                            <td>${reminder.sent_date}</td>
                        `;
                        sentRemindersBody.appendChild(row);
                    });
                } else {
                    sentRemindersTable.style.display = 'none'; // Keep table hidden if no reminders sent
                }
            })
            .catch(error => {
                console.error('Error sending fees reminders:', error);
                reminderResult.textContent = 'Error sending reminders.';
                sentRemindersTable.style.display = 'none'; // Keep sent table hidden on error
            });
    });

    // --- Add Student Functionality --- (Already has toggle logic)
    const showFormBtn = document.getElementById('show-add-student-form-btn');
    const studentForm = document.getElementById('add-student-form');
    const addStudentMessage = document.getElementById('add-student-message');

    if (showFormBtn) {
        showFormBtn.addEventListener('click', () => {
            // Toggle form visibility
            studentForm.style.display = studentForm.style.display === 'none' ? 'block' : 'none';
            addStudentMessage.textContent = ''; // Clear previous messages
            // If closing, reset the form
            if (studentForm.style.display === 'none') {
                studentForm.reset();
            }
        });
    }

    if (studentForm) {
        studentForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent default form submission
            addStudentMessage.textContent = 'Saving...';
            addStudentMessage.style.color = 'black';

            const formData = new FormData(studentForm);
            const studentData = {
                student_name: formData.get('student_name'),
                student_class: formData.get('student_class'),
                parent_name: formData.get('parent_name'),
                parent_email: formData.get('parent_email'),
                parent_phone: formData.get('parent_phone'),
                // Add fee details
                fee_amount: formData.get('fee_amount'),
                fee_due_date: formData.get('fee_due_date')
            };

            // Filter out empty optional fee fields before sending
            const payload = {};
            for (const key in studentData) {
                if (studentData[key] !== null && studentData[key] !== '') {
                    payload[key] = studentData[key];
                }
            }

            fetch('/api/add-student', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload), // Send filtered payload
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error + (data.details ? `: ${data.details}` : ''));
                }
                addStudentMessage.textContent = data.message || 'Student added successfully!';
                addStudentMessage.style.color = 'green';
                studentForm.reset(); // Clear the form
                studentForm.style.display = 'none'; // Hide form after success
            })
            .catch(error => {
                console.error('Error adding student:', error);
                addStudentMessage.textContent = `Error: ${error.message}`;
                addStudentMessage.style.color = 'red';
            });
        });
    }

    // --- Student Details Functionality ---
    const fetchStudentsButton = document.getElementById('fetch-students-button');
    const studentDetailsStatus = document.getElementById('student-details-status');
    const studentDetailsTable = document.getElementById('student-details-table');
    const studentDetailsBody = document.getElementById('student-details-body');
    let studentDetailsVisible = false;

    // Function to fetch and display students
    function fetchAndDisplayStudents() {
        if (studentDetailsVisible) {
            // Hide elements
            studentDetailsStatus.textContent = "";
            studentDetailsBody.innerHTML = '';
            studentDetailsTable.style.display = 'none';
            studentDetailsVisible = false;
        } else {
            // Fetch and display
            studentDetailsStatus.textContent = "Fetching student details...";
            studentDetailsStatus.style.color = 'black'; // Reset color
            studentDetailsBody.innerHTML = ''; // Clear previous results
            studentDetailsTable.style.display = 'none'; // Hide table initially

            fetch('/api/students')
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errData => {
                            throw new Error(`HTTP error! status: ${response.status}. Details: ${errData.details || errData.error || 'Unknown error'}`);
                        }).catch(() => {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (Array.isArray(data) && data.length > 0) {
                        studentDetailsStatus.textContent = `Found ${data.length} students.`;
                        studentDetailsTable.style.display = 'table';
                        data.forEach(student => {
                            const row = document.createElement("tr");
                            row.setAttribute('data-student-id', student.student_id);
                            row.innerHTML = `
                                <td>${student.student_id}</td>
                                <td>${student.student_name}</td>
                                <td>${student.student_class || 'N/A'}</td>
                                <td>${student.parent_name}</td>
                                <td>${student.parent_email}</td>
                                <td>${student.parent_phone || 'N/A'}</td>
                                <td>
                                    <button class="delete-student-btn" data-id="${student.student_id}">Delete</button>
                                </td>
                            `;
                            studentDetailsBody.appendChild(row);
                        });
                        studentDetailsVisible = true; // Mark as visible
                    } else if (Array.isArray(data) && data.length === 0) {
                        studentDetailsStatus.textContent = "No students found.";
                        studentDetailsTable.style.display = 'none';
                        studentDetailsVisible = false;
                    } else {
                        const errorMessage = data.error ? `${data.error}: ${data.details}` : "Received unexpected data format.";
                        studentDetailsStatus.textContent = `Error: ${errorMessage}`;
                        studentDetailsTable.style.display = 'none';
                        studentDetailsVisible = false;
                    }
                })
                .catch(error => {
                    console.error("Error fetching students:", error);
                    studentDetailsStatus.textContent = `Error fetching students: ${error.message}`;
                    studentDetailsStatus.style.color = 'red';
                    studentDetailsTable.style.display = 'none';
                    studentDetailsVisible = false;
                });
        }
    }

    if (fetchStudentsButton) {
        fetchStudentsButton.addEventListener('click', fetchAndDisplayStudents);
    }

    if (studentDetailsBody) {
        studentDetailsBody.addEventListener('click', (event) => {
            if (event.target.classList.contains('delete-student-btn')) {
                const button = event.target;
                const studentId = button.dataset.id;
                const studentName = button.closest('tr').cells[1].textContent; // Get name from table cell

                if (confirm(`Are you sure you want to delete student ${studentName} (ID: ${studentId})? This action cannot be undone.`)) {
                    studentDetailsStatus.textContent = `Deleting student ${studentName}...`;
                    studentDetailsStatus.style.color = 'black';

                    fetch(`/api/delete-student/${studentId}`, {
                        method: 'DELETE',
                    })
                    .then(response => {
                        const status = response.status;
                        return response.json().then(data => ({ status, data }));
                    })
                    .then(({ status, data }) => {
                        if (status === 200) {
                            studentDetailsStatus.textContent = data.message || `Student ${studentName} deleted successfully.`;
                            studentDetailsStatus.style.color = 'green';
                            const rowToRemove = studentDetailsBody.querySelector(`tr[data-student-id="${studentId}"]`);
                            if (rowToRemove) {
                                rowToRemove.remove();
                            }
                            // Update visibility state if the table becomes empty
                            if (studentDetailsBody.children.length === 0) {
                                studentDetailsTable.style.display = 'none';
                                studentDetailsStatus.textContent = "No students remaining.";
                                studentDetailsVisible = false;
                            } else {
                                // Update count in status message
                                studentDetailsStatus.textContent = `Found ${studentDetailsBody.children.length} students.`;
                            }
                        } else {
                            throw new Error(data.details || data.error || `Failed to delete student (Status: ${status})`);
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting student:', error);
                        studentDetailsStatus.textContent = `Error deleting student: ${error.message}`;
                        studentDetailsStatus.style.color = 'red';
                    });
                }
            }
        });
    }
});