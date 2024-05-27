async function sendMessage() {
    const userInput = document.getElementById('userInput').value.trim();
    if (!userInput) return;

    // Display user message
    const messages = document.getElementById('messages');
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user');
    userMessage.innerHTML = `<div class="content">${userInput}</div>`;
    messages.appendChild(userMessage);

    // Send user message to Rasa server
    const response = await fetch('http://localhost:5005/webhooks/rest/webhook', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    });

    const data = await response.json();

    // Display bot response
    data.forEach((msg) => {
        const botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot');
        botMessage.innerHTML = `<img src="images/bot-profile.png" alt="Bot"><div class="content">${msg.text}</div>`;
        messages.appendChild(botMessage);
    });

    // Clear input
    const inputField = document.getElementById('userInput');
    inputField.value = '';
    document.getElementById('sendButton').classList.remove('active');
    messages.scrollTop = messages.scrollHeight;
}

document.getElementById('sendButton').addEventListener('click', sendMessage);

// Enable sending message on pressing Enter key
document.getElementById('userInput').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.getElementById('sendButton').click();
    }
});

// Adjust send button opacity based on input
document.getElementById('userInput').addEventListener('input', function() {
    const userInput = document.getElementById('userInput').value.trim();
    const sendButton = document.getElementById('sendButton');
    if (userInput.length > 0) {
        sendButton.classList.add('active');
    } else {
        sendButton.classList.remove('active');
    }
});
