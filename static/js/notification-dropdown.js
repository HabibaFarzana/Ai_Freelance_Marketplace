import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

function NotificationDropdown() {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  const dropdownRef = useRef(null);
  
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // Fetch every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = () => {
    fetch('/api/notifications/')
      .then(response => response.json())
      .then(data => setNotifications(data));
  };

  const handleNotificationClick = (notificationId, url) => {
    fetch(`/api/notifications/${notificationId}/mark-read/`, { method: 'POST' })
      .then(() => {
        setNotifications(notifications.filter(n => n.id !== notificationId));
        window.location.href = url;
      });
  };

  return (
    <div className="dropdown">
      <button className="btn btn-secondary dropdown-toggle" type="button" onClick={() => setIsOpen(!isOpen)}>
        Notifications {notifications.length > 0 && <span className="badge bg-danger">{notifications.length}</span>}
      </button>
      {isOpen && (
        <ul className="dropdown-menu show">
          {notifications.length === 0 ? (
            <li><a className="dropdown-item" href="#">No new notifications</a></li>
          ) : (
            notifications.map(notification => (
              <li key={notification.id}>
                <a 
                  className="dropdown-item" 
                  href="#" 
                  onClick={() => handleNotificationClick(notification.id, notification.url)}
                >
                  {notification.message}
                </a>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}

ReactDOM.render(<NotificationDropdown />, document.getElementById('notification-dropdown'));