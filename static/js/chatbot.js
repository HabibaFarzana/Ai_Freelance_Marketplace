const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/chatbot/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,  // Include CSRF token in the headers
    },
    body: JSON.stringify({
        message: "Hello, Chatbot!"
    })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
