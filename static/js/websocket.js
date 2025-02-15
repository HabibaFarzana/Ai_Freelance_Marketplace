// static/js/websocket.js
document.addEventListener('DOMContentLoaded', function() {
    const conversationId = document.getElementById('conversation-id').value;
    const currentUsername = document.getElementById('current-username').value;
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const messageContainer = document.getElementById('message-container');

    // WebSocket connection
    const chatSocket = new WebSocket(
        (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + 
        window.location.host + 
        '/ws/chat/' + conversationId + '/'
    );

    // Send message function
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        }
    }

    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Receive messages
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(data.sender === currentUsername ? 'sent' : 'received');
        messageElement.innerHTML = `
            <p>${data.message}</p>
            <small class="text-muted">${new Date(data.timestamp).toLocaleString()}</small>
        `;
        messageContainer.appendChild(messageElement);
        
        // Auto-scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    };

    // Error handling
    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
        alert('Connection error. Please refresh the page.');
    };
});