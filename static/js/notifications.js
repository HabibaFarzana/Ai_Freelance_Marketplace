document.addEventListener('DOMContentLoaded', function() {
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationCount = document.getElementById('notification-count');


    const notificationIcon = document.getElementById('notification-icon'); // As


    // Utility function to categorize notifications by timestamp
    function categorizeNotifications(notifications) {
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        const oneWeekAgo = new Date(today);
        oneWeekAgo.setDate(today.getDate() - 7);

        const categories = {
            today: [],
            yesterday: [],
            thisWeek: [],
            earlier: []
        };

        notifications.forEach(notification => {
            const notificationDate = new Date(notification.timestamp);
            
            if (notificationDate.toDateString() === today.toDateString()) {
                categories.today.push(notification);
            } else if (notificationDate.toDateString() === yesterday.toDateString()) {
                categories.yesterday.push(notification);
            } else if (notificationDate > oneWeekAgo) {
                categories.thisWeek.push(notification);
            } else {
                categories.earlier.push(notification);
            }
        });

        return categories;
    }

    // Utility function to format relative time
    function formatRelativeTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} mins ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        return date.toLocaleDateString();
    }

    // Utility function to get icon based on notification type
    function getNotificationIcon(type) {
        switch(type) {
            case 'bid': return '📝';
            case 'file_upload': return '📁';
            case 'project_status': return '✅';
            default: return '🔔';
        }
    }

    function updateNotifications() {
        fetch('/api/notifications/')
            .then(response => response.json())
            .then(notifications => {
                notificationDropdown.innerHTML = ''; // Clear existing notifications

                // No notifications case
                if (notifications.length === 0) {
                    const noNotificationsMsg = document.createElement('div');
                    noNotificationsMsg.className = 'dropdown-item text-muted text-center';
                    noNotificationsMsg.textContent = 'No new notifications';
                    notificationDropdown.appendChild(noNotificationsMsg);
                } else {
                    // Create a scrollable container for notifications
                    const scrollContainer = document.createElement('div');
                    scrollContainer.className = 'notification-scroll-container';
                    scrollContainer.style.maxHeight = '400px';
                    scrollContainer.style.overflowY = 'auto';
                    scrollContainer.style.width = '300px'; // Fixed width for responsiveness

                    // Categorize notifications
                    const categorizedNotifications = categorizeNotifications(notifications);

                    // Create categories
                    const categories = [
                        { key: 'today', label: 'Today' },
                        { key: 'yesterday', label: 'Yesterday' },
                        { key: 'thisWeek', label: 'This Week' },
                        { key: 'earlier', label: 'Earlier' }
                    ];

                    categories.forEach(category => {
                        const categoryNotifications = categorizedNotifications[category.key];
                        
                        if (categoryNotifications.length > 0) {
                            // Category header
                            const categoryHeader = document.createElement('div');
                            categoryHeader.className = 'dropdown-header text-muted text-uppercase small';
                            categoryHeader.textContent = category.label;
                            scrollContainer.appendChild(categoryHeader);

                            // Notifications in this category
                            categoryNotifications.forEach(notification => {
                                const a = document.createElement('a');
                                a.className = 'dropdown-item d-flex align-items-center';
                                a.href = '#';
                                a.dataset.notificationId = notification.id;
                                a.dataset.notificationUrl = notification.url;

                                // Icon and content container
                                const iconSpan = document.createElement('span');
                                iconSpan.className = 'me-3';
                                iconSpan.textContent = getNotificationIcon(notification.type);

                                const contentDiv = document.createElement('div');
                                contentDiv.innerHTML = `
                                    <div class="small">${notification.message}</div>
                                    <div class="text-muted x-small">${formatRelativeTime(notification.timestamp)}</div>
                                `;

                                a.appendChild(iconSpan);
                                a.appendChild(contentDiv);
                                scrollContainer.appendChild(a);
                            });
                        }
                    });

                    // Clear All button
                    if (notifications.length > 0) {
                        const clearAll = document.createElement('div');
                        clearAll.className = 'dropdown-item text-center';
                        clearAll.innerHTML = `
                            <button id="clear-all-notifications" class="btn btn-sm btn-outline-danger">
                                Clear All Notifications
                            </button>
                        `;
                        scrollContainer.appendChild(clearAll);
                    }

                    notificationDropdown.appendChild(scrollContainer);
                }
                
                // Update notification count
                notificationCount.textContent = notifications.length;
                notificationCount.style.display = notifications.length > 0 ? 'inline-block' : 'none';

                // Add event listeners for individual notifications
                notificationDropdown.querySelectorAll('.dropdown-item[data-notification-id]').forEach(item => {
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        const notificationId = this.dataset.notificationId;
                        const url = this.dataset.notificationUrl;
                        
                        // Mark as read
                        fetch(`/api/notifications/${notificationId}/mark-read/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCsrfToken(),
                                'Content-Type': 'application/json',
                            },
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                window.location.href = url;
                            }
                        });
                    });
                });

                // Add event listener for clear all
                const clearAllBtn = document.getElementById('clear-all-notifications');
                if (clearAllBtn) {
                    clearAllBtn.addEventListener('click', clearAllNotifications);
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }

    function clearAllNotifications() {
        fetch('/api/notifications/clear-all/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotifications();
            }
        });
    }

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    

    // Update notifications every 30 seconds
    setInterval(updateNotifications, 30000);

    // Initial update
    updateNotifications();
});