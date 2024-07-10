let socket;
let currentMessage = '';
hljs.highlightAll(); 

document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const submitUpload = document.getElementById('submitUpload');
    const sendBtn = document.getElementById('sendBtn');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const uploadModal = new bootstrap.Modal(document.getElementById('uploadModal'));

    uploadBtn.addEventListener('click', () => uploadModal.show());

    submitUpload.addEventListener('click', uploadFiles);

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function uploadFiles() {
        const fileInput = document.getElementById('fileInput');
        const uploadStatus = document.getElementById('uploadStatus');
        const formData = new FormData();

        for (const file of fileInput.files) {
            formData.append('files', file);
        }

        uploadStatus.textContent = 'Uploading...';

        fetch('http://localhost:8000/upload/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadStatus.textContent = 'Upload successful!';
            setTimeout(() => {
                uploadModal.hide();
                connectWebSocket();
            }, 1500);
        })
        .catch(error => {
            uploadStatus.textContent = 'Upload failed. Please try again.';
            console.error('Error:', error);
        });
    }

    function connectWebSocket() {
        socket = new WebSocket('http://devporta-alb-salpojrsuyvo-261385298.eu-west-1.elb.amazonaws.com/ws/chat');

        socket.onopen = (event) => {
            console.log('WebSocket connected:', event);
        };

        socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event);
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        socket.onmessage = (event) => {
            console.log('Received message:', event.data);
            handleStreamedMessage(event.data);
        };
    }

    function handleStreamedMessage(data) {
        if (data === '\n') {
            // End of message
            displayMessage(currentMessage, 'ai');
            currentMessage = '';
        } else {
            currentMessage += data;
            // Update the last AI message in real-time
            updateLastAIMessage(currentMessage);
        }
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            displayMessage(message, 'user');
            console.log(message)
            socket.send(JSON.stringify({
                user_query: message,
                session_id: 'test001'
            }));
            userInput.value = '';
        }
    }

    function updateLastAIMessage(content) {
        const lastMessage = chatMessages.querySelector('.ai-message:last-child');
        if (lastMessage) {
            lastMessage.innerHTML = marked.parse(content);
            lastMessage.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        } else {
            displayMessage(content, 'ai');
        }
    }

    function displayMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
        
        if (sender === 'ai') {
            const formattedContent = marked.parse(content);
            messageDiv.innerHTML = formattedContent;
            messageDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        } else {
            messageDiv.textContent = content;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});