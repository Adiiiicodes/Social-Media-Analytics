document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const vizContainer = document.getElementById('visualizationContainer');

    // Handle message sending
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Add user message
        addMessage(message, 'user');
        userInput.value = '';

        // Simulate bot response (replace with actual API call later)
        setTimeout(() => {
            // Example bot response with visualization
            if (message.toLowerCase().includes('analytics') || 
                message.toLowerCase().includes('stats') ||
                message.toLowerCase().includes('metrics')) {
                addMessage('Here\'s your social media analytics:', 'bot');
                addVisualization();
            } else {
                addMessage('I can help you analyze your social media performance. Try asking about your analytics, stats, or metrics!', 'bot');
            }
        }, 1000);
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add example visualization (replace with actual data visualization later)
    function addVisualization() {
        const vizDiv = document.createElement('div');
        vizDiv.style.border = '2px solid black';
        vizDiv.style.padding = '1rem';
        vizDiv.style.marginBottom = '1rem';
        vizDiv.style.background = 'white';
        vizDiv.style.boxShadow = '4px 4px 0 black';
        
        vizDiv.innerHTML = `
            <h3 style="margin-bottom: 1rem;">Sample Metrics Visualization</h3>
            <div style="width: 100%; height: 200px; background: #FFE147; 
                        border: 2px solid black; display: flex; 
                        justify-content: center; align-items: center;">
                [Placeholder for actual visualization]
            </div>
        `;
        
        vizContainer.prepend(vizDiv);
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Handle textarea auto-resize
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
});
