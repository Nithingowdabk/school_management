document.addEventListener("DOMContentLoaded", function () {

    // --- Helper Function to Fetch Data --- //
    function fetchData(url, options = {}) {
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    // Try to parse error details from JSON response
                    return response.json().then(errData => {
                        throw new Error(`HTTP error! status: ${response.status}. Details: ${errData.details || errData.error || 'Unknown error'}`);
                    }).catch(() => {
                        // Fallback if response is not JSON or parsing fails
                        throw new Error(`HTTP error! status: ${response.status}. Failed to fetch.`);
                    });
                }
                // Check if response is JSON before parsing
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    return response.json();
                } else {
                    return response.text().then(text => { 
                        // Handle non-JSON success responses if necessary, or treat as unexpected
                        console.warn("Received non-JSON response for", url, text);
                        return { message: text || "Operation successful, but no JSON data returned." }; // Or throw an error
                    }); 
                }
            });
    }

    // --- Teacher Performance Page Logic --- //
    const teacherPerformanceSection = document.getElementById("teacher-performance");
    if (teacherPerformanceSection) {
        const tableBody = document.getElementById("teacher-performance-body");
        const performanceResult = document.getElementById("performance-result");
        const performanceTable = document.getElementById("teacher-performance-table");
        const downloadContainer = document.getElementById("download-container");

        function loadTeacherPerformance() {
            performanceResult.textContent = "Fetching data...";
            performanceResult.style.color = 'black';
            tableBody.innerHTML = '';
            downloadContainer.innerHTML = '';
            if (performanceTable) performanceTable.style.display = 'none';

            fetchData("/api/teacher-performance")
                .then(data => {
                    performanceResult.textContent = data.message;
                    if (data && data.data && data.data.length > 0) {
                        if (performanceTable) performanceTable.style.display = 'table';
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
                    } else if (data && data.data && data.data.length === 0) {
                        performanceResult.textContent = "No teacher performance data found.";
                        if (performanceTable) performanceTable.style.display = 'none';
                    } else {
                        performanceResult.textContent = data.message || "Received unexpected data format.";
                        if (performanceTable) performanceTable.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error("Error fetching teacher performance data:", error);
                    performanceResult.textContent = `Error fetching data: ${error.message}`;
                    performanceResult.style.color = 'red';
                    if (performanceTable) performanceTable.style.display = 'none';
                });
        }
        // Load data automatically when the page loads
        loadTeacherPerformance();
    }

    // --- Fees Management Page Logic --- //
    const feesReminderSection = document.getElementById("fees-reminder");
    if (feesReminderSection) {
        const pendingFeesStatus = document.getElementById('pending-fees-status');
        const pendingFeesDisplayTable = document.getElementById('pending-fees-display-table');
        const pendingFeesDisplayBody = document.getElementById('pending-fees-display-body');
        const sendAllRemindersButton = document.getElementById('send-all-reminders-button');
        const reminderResult = document.getElementById('reminder-result');
        const sentRemindersTable = document.getElementById('sent-reminders-table');
        const sentRemindersBody = document.getElementById('sent-reminders-body');

        function loadPendingFees() {
            pendingFeesStatus.textContent = "Fetching pending fees...";
            pendingFeesStatus.style.color = 'black';
            pendingFeesDisplayBody.innerHTML = '';
            if (pendingFeesDisplayTable) pendingFeesDisplayTable.style.display = 'none';
            if (sendAllRemindersButton) sendAllRemindersButton.style.display = 'none';
            if (sentRemindersTable) sentRemindersTable.style.display = 'none';
            reminderResult.textContent = '';

            fetchData('/api/pending-fees')
                .then(data => {
                    if (Array.isArray(data) && data.length > 0) {
                        pendingFeesStatus.textContent = `Found ${data.length} pending fee records.`;
                        if (pendingFeesDisplayTable) pendingFeesDisplayTable.style.display = 'table';
                        if (sendAllRemindersButton) sendAllRemindersButton.style.display = 'block';
                        data.forEach(record => {
                            const row = document.createElement("tr");
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
                    } else if (Array.isArray(data) && data.length === 0) {
                        pendingFeesStatus.textContent = "No pending fee records found.";
                        if (pendingFeesDisplayTable) pendingFeesDisplayTable.style.display = 'none';
                        if (sendAllRemindersButton) sendAllRemindersButton.style.display = 'none';
                    } else {
                        // Error handled by fetchData, but display message if needed
                        pendingFeesStatus.textContent = data.message || "Received unexpected data format.";
                        pendingFeesStatus.style.color = 'red';
                        if (pendingFeesDisplayTable) pendingFeesDisplayTable.style.display = 'none';
                        if (sendAllRemindersButton) sendAllRemindersButton.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error("Error fetching pending fees:", error);
                    pendingFeesStatus.textContent = `Error fetching pending fees: ${error.message}`;
                    pendingFeesStatus.style.color = 'red';
                    if (pendingFeesDisplayTable) pendingFeesDisplayTable.style.display = 'none';
                    if (sendAllRemindersButton) sendAllRemindersButton.style.display = 'none';
                });
        }

        // Event listener for sending all reminders
        if (sendAllRemindersButton) {
            sendAllRemindersButton.addEventListener('click', () => {
                reminderResult.textContent = "Processing and sending reminders...";
                reminderResult.style.color = 'black';
                sentRemindersBody.innerHTML = '';
                if (sentRemindersTable) sentRemindersTable.style.display = 'none';

                fetchData('/api/send-all-reminders', { method: 'POST' })
                    .then(data => {
                        reminderResult.textContent = data.message;
                        if (data.reminders_sent_details && data.reminders_sent_details.length > 0) {
                            if (sentRemindersTable) sentRemindersTable.style.display = 'table';
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
                            if (sentRemindersTable) sentRemindersTable.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Error sending fees reminders:', error);
                        reminderResult.textContent = `Error sending reminders: ${error.message}`;
                        reminderResult.style.color = 'red';
                        if (sentRemindersTable) sentRemindersTable.style.display = 'none';
                    });
            });
        }

        // Event listener for "Mark as Paid" buttons
        if (pendingFeesDisplayBody) {
            pendingFeesDisplayBody.addEventListener('click', (event) => {
                if (event.target.classList.contains('mark-paid-btn')) {
                    const button = event.target;
                    const feeId = button.dataset.feeId;
                    const row = button.closest('tr');
                    const studentName = row.cells[0].textContent;

                    if (confirm(`Are you sure you want to mark the fee for ${studentName} (ID: ${feeId}) as paid? This will remove the record.`)) {
                        pendingFeesStatus.textContent = `Marking fee ${feeId} as paid...`;
                        pendingFeesStatus.style.color = 'black';

                        fetchData(`/api/mark-fee-paid/${feeId}`, { method: 'DELETE' })
                            .then(data => {
                                pendingFeesStatus.textContent = data.message || `Fee ${feeId} marked as paid successfully.`;
                                pendingFeesStatus.style.color = 'green';
                                row.remove();

                                const remainingRows = pendingFeesDisplayBody.children.length;
                                if (remainingRows === 0) {
                                    if (pendingFeesDisplayTable) pendingFeesDisplayTable.style.display = 'none';
                                    if (sendAllRemindersButton) sendAllRemindersButton.style.display = 'none';
                                    pendingFeesStatus.textContent = "No pending fee records remaining.";
                                } else {
                                    pendingFeesStatus.textContent = `Found ${remainingRows} pending fee records.`;
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
        }

        // Load data automatically when the page loads
        loadPendingFees();
    }

    // --- Add Student Page Logic --- //
    const addStudentSection = document.getElementById("add-student-section");
    if (addStudentSection) {
        const studentForm = document.getElementById('add-student-form');
        const addStudentMessage = document.getElementById('add-student-message');

        if (studentForm) {
            studentForm.addEventListener('submit', (event) => {
                event.preventDefault();
                addStudentMessage.textContent = 'Saving...';
                addStudentMessage.style.color = 'black';

                const formData = new FormData(studentForm);
                const studentData = {
                    student_name: formData.get('student_name'),
                    student_class: formData.get('student_class'),
                    parent_name: formData.get('parent_name'),
                    parent_email: formData.get('parent_email'),
                    parent_phone: formData.get('parent_phone'),
                    fee_amount: formData.get('fee_amount'),
                    fee_due_date: formData.get('fee_due_date')
                };

                const payload = {};
                for (const key in studentData) {
                    if (studentData[key] !== null && studentData[key] !== '') {
                        payload[key] = studentData[key];
                    }
                }

                fetchData('/api/add-student', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                })
                .then(data => {
                    addStudentMessage.textContent = data.message || 'Student added successfully!';
                    addStudentMessage.style.color = 'green';
                    studentForm.reset();
                    // Optionally redirect or give further instructions
                    // window.location.href = '/student-details.html'; // Example redirect
                })
                .catch(error => {
                    console.error('Error adding student:', error);
                    addStudentMessage.textContent = `Error: ${error.message}`;
                    addStudentMessage.style.color = 'red';
                });
            });
        }
    }

    // --- Student Details Page Logic --- //
    const studentDetailsSection = document.getElementById("student-details-section");
    if (studentDetailsSection) {
        const studentDetailsStatus = document.getElementById('student-details-status');
        const studentDetailsTable = document.getElementById('student-details-table');
        const studentDetailsBody = document.getElementById('student-details-body');

        function loadStudentDetails() {
            studentDetailsStatus.textContent = "Fetching student details...";
            studentDetailsStatus.style.color = 'black';
            studentDetailsBody.innerHTML = '';
            if (studentDetailsTable) studentDetailsTable.style.display = 'none';

            fetchData('/api/students')
                .then(data => {
                    if (Array.isArray(data) && data.length > 0) {
                        studentDetailsStatus.textContent = `Found ${data.length} students.`;
                        if (studentDetailsTable) studentDetailsTable.style.display = 'table';
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
                    } else if (Array.isArray(data) && data.length === 0) {
                        studentDetailsStatus.textContent = "No students found.";
                        if (studentDetailsTable) studentDetailsTable.style.display = 'none';
                    } else {
                        studentDetailsStatus.textContent = data.message || "Received unexpected data format.";
                        studentDetailsStatus.style.color = 'red';
                        if (studentDetailsTable) studentDetailsTable.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error("Error fetching students:", error);
                    studentDetailsStatus.textContent = `Error fetching students: ${error.message}`;
                    studentDetailsStatus.style.color = 'red';
                    if (studentDetailsTable) studentDetailsTable.style.display = 'none';
                });
        }

        // Event listener for delete buttons
        if (studentDetailsBody) {
            studentDetailsBody.addEventListener('click', (event) => {
                if (event.target.classList.contains('delete-student-btn')) {
                    const button = event.target;
                    const studentId = button.dataset.id;
                    const row = button.closest('tr');
                    const studentName = row.cells[1].textContent;

                    if (confirm(`Are you sure you want to delete student ${studentName} (ID: ${studentId})? This action cannot be undone.`)) {
                        studentDetailsStatus.textContent = `Deleting student ${studentName}...`;
                        studentDetailsStatus.style.color = 'black';

                        fetchData(`/api/delete-student/${studentId}`, { method: 'DELETE' })
                            .then(data => {
                                studentDetailsStatus.textContent = data.message || `Student ${studentName} deleted successfully.`;
                                studentDetailsStatus.style.color = 'green';
                                row.remove();

                                const remainingRows = studentDetailsBody.children.length;
                                if (remainingRows === 0) {
                                    if (studentDetailsTable) studentDetailsTable.style.display = 'none';
                                    studentDetailsStatus.textContent = "No students remaining.";
                                } else {
                                    studentDetailsStatus.textContent = `Found ${remainingRows} students.`;
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

        // Load data automatically when the page loads
        loadStudentDetails();
    }
});