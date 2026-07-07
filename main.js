// DailyTrack JavaScript Functions

/**
 * Toggle task completion via AJAX
 */
function toggleTask(taskId) {
    fetch(`/tasks/${taskId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
            if (taskElement) {
                taskElement.classList.toggle('completed');
            }
            // Update completion percentage display
            updateCompletionBar(data.completion_percent);
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Update the daily completion bar
 */
function updateCompletionBar(percentage) {
    const bar = document.querySelector('.progress-bar');
    if (bar) {
        bar.style.width = percentage + '%';
        bar.textContent = Math.round(percentage) + '%';
    }
}

/**
 * Format date for display
 */
function formatDate(date) {
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

/**
 * Show confirmation dialog
 */
function showConfirmDialog(message) {
    return confirm(message);
}

/**
 * Display flash message
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Validate file upload size
 */
function validateFileSize(file, maxSizeMB = 20) {
    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
        showNotification(`File too large. Maximum size is ${maxSizeMB}MB.`, 'danger');
        return false;
    }
    return true;
}

/**
 * Validate file type
 */
function validateFileType(file, allowedTypes = ['image/jpeg', 'image/png', 'video/mp4', 'video/quicktime']) {
    if (!allowedTypes.includes(file.type)) {
        showNotification(`File type not allowed. Allowed types: images and videos.`, 'danger');
        return false;
    }
    return true;
}

/**
 * Initialize file input listeners
 */
function initializeFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                if (!validateFileType(file)) {
                    this.value = '';
                } else if (!validateFileSize(file)) {
                    this.value = '';
                }
            }
        });
    });
}

/**
 * Initialize task checkboxes
 */
function initializeTaskCheckboxes() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            toggleTask(taskId);
        });
    });
}

/**
 * Initialize recurring task toggle
 */
function initializeRecurringToggle() {
    const recurringCheckbox = document.getElementById('is_recurring');
    if (recurringCheckbox) {
        recurringCheckbox.addEventListener('change', function() {
            const recurrenceType = document.getElementById('recurrence-type');
            if (recurrenceType) {
                recurrenceType.style.display = this.checked ? 'block' : 'none';
            }
        });
    }
}

/**
 * Clear form inputs
 */
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Smooth scroll to element
 */
function smoothScroll(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Initialize dark mode toggle
 */
function initializeDarkMode() {
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            // Save preference to localStorage
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
    }
    
    // Load saved preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
}

/**
 * Initialize all interactive elements
 */
function initializeApp() {
    initializeTaskCheckboxes();
    initializeFileInputs();
    initializeRecurringToggle();
    initializeDarkMode();
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);

// Auto-refresh completion bar every 30 seconds
setInterval(function() {
    // Could fetch updated completion percentage here
}, 30000);
