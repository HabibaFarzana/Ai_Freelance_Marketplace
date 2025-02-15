document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.querySelector('.btn-primary');
    const messageContainer = document.getElementById('message-container');
    const conversationId = document.getElementById('conversation-id')?.value;
    const currentUsername = document.getElementById('current-username')?.value;

    if (!conversationId || !currentUsername) {
        console.error('Missing required conversation data');
        return;
    }

    // Create WebSocket connection
    const chatSocket = new WebSocket(
        `ws://${window.location.host}/ws/chat/${conversationId}/`
    );

    chatSocket.onopen = function(e) {
        console.log('WebSocket connection established');
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        appendMessage(data);
    };

    chatSocket.onclose = function(e) {
        console.error('WebSocket connection closed');
    };

    chatSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    function appendMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.sender === currentUsername ? 'sent' : 'received'}`;
        
        const content = document.createElement('p');
        content.textContent = data.message;
        
        const timestamp = document.createElement('small');
        timestamp.className = 'text-muted';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(content);
        messageDiv.appendChild(timestamp);
        messageContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        }
    }

    // Send message on button click
    sendButton.addEventListener('click', function(e) {
        e.preventDefault();
        sendMessage();
    });

    // Send message on Enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
