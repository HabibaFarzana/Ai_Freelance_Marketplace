// file-sharing.js
document.addEventListener('DOMContentLoaded', function() {
    // Ensure the event listener is only attached once
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return; // Exit if form doesn't exist
    
    // Remove any existing event listeners by cloning and replacing the form
    const newUploadForm = uploadForm.cloneNode(true);
    uploadForm.parentNode.replaceChild(newUploadForm, uploadForm);
    
    const fileInput = document.getElementById('file-input');
    const submitButton = newUploadForm.querySelector('button[type="submit"]');
    let isUploading = false;
    
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        const container = newUploadForm.closest('.card-body');
        
        // Remove existing alerts
        const existingAlerts = container.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }

    function disableForm(disable) {
        fileInput.disabled = disable;
        submitButton.disabled = disable;
        submitButton.textContent = disable ? 'Uploading...' : 'Upload File';
    }

    // Single event listener for form submission
    newUploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (isUploading) {
            console.log('Upload already in progress');
            return;
        }
        
        const projectId = this.dataset.projectId;
        const file = fileInput.files[0];
        
        if (!file) {
            showAlert('Please select a file first', 'warning');
            return;
        }

        if (file.size > 50 * 1024 * 1024) {
            showAlert('File size exceeds 50MB limit', 'warning');
            return;
        }

        isUploading = true;
        disableForm(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`/api/projects/${projectId}/files/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showAlert('File uploaded successfully!', 'success');
                fileInput.value = ''; // Clear the file input
                // Refresh the file list without reloading the page
                await refreshFileList(projectId);
            } else {
                throw new Error(data.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert(error.message || 'Error uploading file', 'danger');
        } finally {
            isUploading = false;
            disableForm(false);
        }
    });

    async function refreshFileList(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}/files/`);
            const data = await response.json();
            if (data.files) {
                const fileList = document.getElementById('file-list');
                if (!fileList) return;
                
                fileList.innerHTML = ''; // Clear existing list
                data.files.forEach(file => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center';
                    li.innerHTML = `
                        <div>
                            <strong>${file.name}</strong>
                            <br>
                            <small class="text-muted">
                                Uploaded by ${file.uploaded_by} on ${new Date(file.uploaded_at).toLocaleString()}
                            </small>
                        </div>
                        <div class="btn-group">
                            <a href="/files/${file.id}/download/" class="btn btn-primary btn-sm">
                                <i class="fas fa-download"></i> Download
                            </a>
                            ${file.can_delete ? `
                                <button class="btn btn-danger btn-sm delete-file" data-file-id="${file.id}">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            ` : ''}
                        </div>
                    `;
                    fileList.appendChild(li);
                });
            }
        } catch (error) {
            console.error('Error refreshing file list:', error);
        }
    }
});