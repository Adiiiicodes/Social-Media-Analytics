document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const vizSection = document.getElementById('visualizationSection');
    const vizContainer = document.getElementById('visualizationContainer');

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Add user message
        addMessage(message, 'user');
        userInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Add AI response
            addMessage(data.response.text, 'bot');

            // Handle visualization
            if (data.should_show_viz) {
                showVisualization();
                addVisualization(data.response);
            } else {
                hideVisualization();
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request.', 'bot');
        }
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showVisualization() {
        vizSection.classList.add('active');
    }

    function hideVisualization() {
        vizSection.classList.remove('active');
        setTimeout(() => {
            vizContainer.innerHTML = '';
        }, 300);
    }

    function addVisualization(data) {
        const vizDiv = document.createElement('div');
        vizDiv.classList.add('viz-card');
        vizDiv.innerHTML = parseDataToVisualization(data);
        vizContainer.prepend(vizDiv);
    }

    function parseDataToVisualization(data) {
        // Parse the response and create appropriate visualization
        // This is a placeholder - implement actual visualization logic
        return `
            <h3>Analysis Results</h3>
            <div class="viz-content">
                ${data.text}
            </div>
        `;
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
});
