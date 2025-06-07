document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    const fileInput = document.getElementById('excel_file');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const selectedFileInfo = document.getElementById('selectedFileInfo');
    const selectedFileName = document.getElementById('selectedFileName');
    const selectedFileSize = document.getElementById('selectedFileSize');
    const batchSubmitBtn = document.getElementById('batchSubmitBtn');
    const batchForm = document.getElementById('batchForm');
    const uploadProgress = document.getElementById('uploadProgress');

    // Drag and drop functionality
    if (fileUploadArea) {
        fileUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileUploadArea.classList.add('dragover');
        });

        fileUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            fileUploadArea.classList.remove('dragover');
        });

        fileUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            fileUploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelection(files[0]);
            }
        });

        // Click to upload
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });
    }

    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }

    function handleFileSelection(file) {
        // Validate file type
        const allowedTypes = ['.xlsx', '.xls', '.csv'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            alert('Please select a valid file (.xlsx, .xls, or .csv)');
            clearSelectedFile();
            return;
        }

        // Validate file size (16MB = 16 * 1024 * 1024 bytes)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('File size must be less than 16MB');
            clearSelectedFile();
            return;
        }

        // Display selected file info
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatFileSize(file.size);
        selectedFileInfo.style.display = 'block';
        batchSubmitBtn.disabled = false;
        
        // Hide the upload area
        fileUploadArea.style.display = 'none';
    }

    // Clear selected file
    window.clearSelectedFile = function() {
        fileInput.value = '';
        selectedFileInfo.style.display = 'none';
        fileUploadArea.style.display = 'block';
        batchSubmitBtn.disabled = true;
        uploadProgress.classList.remove('show');
    };

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Form submission with progress
    if (batchForm) {
        batchForm.addEventListener('submit', function(e) {
            // Show progress bar
            uploadProgress.classList.add('show');
            batchSubmitBtn.disabled = true;
            batchSubmitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            // Simulate progress (since we can't track actual upload progress easily)
            let progress = 0;
            const progressBar = uploadProgress.querySelector('.progress-bar');
            
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressBar.style.width = progress + '%';
            }, 200);

            // Clear interval after 10 seconds (fallback)
            setTimeout(() => {
                clearInterval(interval);
                progressBar.style.width = '100%';
            }, 10000);
        });
    }

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Tooltip initialization
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Form validation for single prediction
    const singleForm = document.querySelector('#single-prediction form');
    if (singleForm) {
        singleForm.addEventListener('submit', function(e) {
            const submitBtn = singleForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Predicting...';
            
            // Re-enable after a delay (in case of error)
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Predict Churn';
            }, 5000);
        });
    }

    // Tab switching analytics (optional)
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(e) {
            console.log('Switched to tab:', e.target.getAttribute('data-bs-target'));
        });
    });
});
