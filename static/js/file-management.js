// file-management.js
(() => {
    // Enhanced state management
    const state = {
        pendingDeletions: new Set(), // Track files currently being deleted
        deletedFileIds: new Set()    // Track successfully deleted files
    };

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showAlert(message, type) {
        // Remove any existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert alert at the top of the container
        const container = document.querySelector('.container');
        if (container && container.firstChild) {
            container.insertBefore(alertDiv, container.firstChild);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => alertDiv.remove(), 5000);
    }

    async function handleFileDeletion(fileId, button) {
        // Prevent deletion if already in progress or file was already deleted
        if (state.pendingDeletions.has(fileId) || state.deletedFileIds.has(fileId)) {
            return;
        }

        try {
            // Add to pending deletions and disable button
            state.pendingDeletions.add(fileId);
            button.disabled = true;

            const response = await fetch(`/api/files/${fileId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to delete file');
            }

            // Mark file as successfully deleted
            state.deletedFileIds.add(fileId);
            
            // Remove the file element from DOM
            const listItem = button.closest('.list-group-item');
            if (listItem) {
                listItem.remove();
                showAlert('File deleted successfully', 'success');
            }

        } catch (error) {
            console.error('Error during file deletion:', error);
            showAlert(error.message, 'danger');
            button.disabled = false;
        } finally {
            // Remove from pending deletions
            state.pendingDeletions.delete(fileId);
        }
    }

    // Single event listener for delete buttons using event delegation
    document.addEventListener('click', (event) => {
        const deleteButton = event.target.closest('.delete-file');
        if (!deleteButton) return;

        event.preventDefault();
        event.stopPropagation();

        const fileId = deleteButton.dataset.fileId;
        if (!fileId) return;

        // Show confirmation dialog and handle deletion
        if (window.confirm('Are you sure you want to delete this file?')) {
            handleFileDeletion(fileId, deleteButton)
                .catch(error => console.error('Deletion handler error:', error));
        }
    });
})();