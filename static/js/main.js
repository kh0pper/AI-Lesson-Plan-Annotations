// Main JavaScript for AI Lesson Plan Annotator

document.addEventListener('DOMContentLoaded', function() {
    // File validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (16MB = 16 * 1024 * 1024 bytes)
                const maxSize = 16 * 1024 * 1024;
                if (file.size > maxSize) {
                    alert('File size must be less than 16MB');
                    this.value = '';
                    return;
                }
                
                // Check file type
                if (file.type !== 'application/pdf') {
                    alert('Please select a PDF file');
                    this.value = '';
                    return;
                }
                
                // Show file name
                console.log('Selected file:', file.name, 'Size:', (file.size / 1024 / 1024).toFixed(2) + 'MB');
            }
        });
    }
    
    // Form submission handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            if (!fileInput.files[0]) {
                e.preventDefault();
                alert('Please select a PDF file to upload');
                return;
            }
            
            // Show processing state
            const submitBtn = document.getElementById('submitBtn');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // Preset change handling
    const presetSelect = document.getElementById('preset');
    if (presetSelect) {
        presetSelect.addEventListener('change', function() {
            toggleCustomParameters();
        });
    }
    
    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.querySelector('.btn-close')) {
                alert.querySelector('.btn-close').click();
            }
        });
    }, 5000);
});

function toggleCustomParameters() {
    const preset = document.getElementById('preset').value;
    const customParams = document.getElementById('customParameters');
    
    if (customParams) {
        if (preset === 'custom') {
            customParams.style.display = 'block';
            customParams.scrollIntoView({ behavior: 'smooth' });
        } else {
            customParams.style.display = 'none';
        }
    }
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}