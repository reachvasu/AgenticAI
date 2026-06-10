// Display selected file name
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('fileName');
    
    fileInput.addEventListener('change', function(e) {
        fileNameDisplay.textContent = e.target.files[0]?.name || 'PDF or DOCX (Max 10MB)';
    });
});
