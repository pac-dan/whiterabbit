/**
 * AI Chat Widget with Socket.IO
 * Powered by Claude AI via Anthropic API
 */

(function() {
    'use strict';

    // Chat state
    let socket = null;
    let sessionId = null;
    let isConnected = false;
    let isTyping = false;

    // DOM elements
    const chatToggle = document.getElementById('chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const chatClose = document.getElementById('chat-close');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    /**
     * Initialize chat widget
     */
    function initChat() {
        // Toggle chat window
        chatToggle.addEventListener('click', function() {
            chatWindow.classList.toggle('hidden');

            // Connect to socket when chat is opened for the first time
            if (!isConnected && !chatWindow.classList.contains('hidden')) {
                connectToChat();
            }

            // Focus input when opening
            if (!chatWindow.classList.contains('hidden')) {
                chatInput.focus();
            }
        });

        // Close chat window
        chatClose.addEventListener('click', function() {
            chatWindow.classList.add('hidden');
        });

        // Handle chat form submission
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }

    /**
     * Connect to Socket.IO chat server
     */
    function connectToChat() {
        if (isConnected) return;

        console.log('Connecting to chat server...');

        // Connect to chat namespace
        socket = io('/chat', {
            transports: ['websocket', 'polling']
        });

        // Connection established
        socket.on('connect', function() {
            console.log('Connected to chat server');
            isConnected = true;
        });

        // Receive session ID
        socket.on('connected', function(data) {
            sessionId = data.session_id;
            console.log('Chat session ID:', sessionId);
        });

        // Handle AI typing indicator
        socket.on('ai_typing', function(data) {
            if (data.typing) {
                showTypingIndicator();
            } else {
                hideTypingIndicator();
            }
        });

        // Handle user message echo
        socket.on('user_message', function(data) {
            // User message already displayed when sent
        });

        // Handle AI response chunks (streaming)
        let currentMessageDiv = null;

        socket.on('ai_response_chunk', function(data) {
            if (!currentMessageDiv) {
                // Create new message div for AI response
                currentMessageDiv = createAIMessageElement('');
                chatMessages.appendChild(currentMessageDiv);
                scrollToBottom();
            }

            // Append chunk to message
            const messageText = currentMessageDiv.querySelector('p');
            messageText.textContent += data.chunk;
            scrollToBottom();
        });

        // Handle complete AI response
        socket.on('ai_response_complete', function(data) {
            currentMessageDiv = null;
            hideTypingIndicator();
            scrollToBottom();
        });

        // Handle errors
        socket.on('error', function(data) {
            hideTypingIndicator();
            addSystemMessage(data.message || 'An error occurred', 'error');
        });

        // Handle disconnection
        socket.on('disconnect', function() {
            console.log('Disconnected from chat server');
            isConnected = false;
            addSystemMessage('Disconnected from chat. Please refresh to reconnect.', 'warning');
        });
    }

    /**
     * Send message to AI
     */
    function sendMessage() {
        const message = chatInput.value.trim();

        if (!message || !isConnected) return;

        // Display user message
        addUserMessage(message);

        // Send to server
        socket.emit('send_message', {
            session_id: sessionId,
            message: message
        });

        // Clear input
        chatInput.value = '';
        chatInput.focus();
    }

    /**
     * Add user message to chat
     */
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start space-x-2 justify-end';

        messageDiv.innerHTML = `
            <div class="bg-blue-600 text-white p-3 rounded-lg shadow-sm max-w-[80%]">
                <p class="text-sm">${escapeHtml(message)}</p>
            </div>
            <div class="bg-gray-200 text-gray-700 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-user"></i>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    /**
     * Create AI message element
     */
    function createAIMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start space-x-2';

        messageDiv.innerHTML = `
            <div class="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot"></i>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm max-w-[80%]">
                <p class="text-sm">${escapeHtml(message)}</p>
            </div>
        `;

        return messageDiv;
    }

    /**
     * Show typing indicator
     */
    function showTypingIndicator() {
        if (isTyping) return;

        isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'flex items-start space-x-2';

        typingDiv.innerHTML = `
            <div class="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot"></i>
            </div>
            <div class="bg-white p-3 rounded-lg shadow-sm">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
            </div>
        `;

        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        isTyping = false;
    }

    /**
     * Add system message
     */
    function addSystemMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'text-center my-2';

        const colorClass = type === 'error' ? 'text-red-600' : type === 'warning' ? 'text-yellow-600' : 'text-gray-500';

        messageDiv.innerHTML = `
            <p class="text-xs ${colorClass}">${escapeHtml(message)}</p>
        `;

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    /**
     * Scroll chat to bottom
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear chat history
     */
    window.clearChatHistory = function() {
        if (socket && isConnected) {
            socket.emit('clear_history', {
                session_id: sessionId
            });

            // Clear UI
            chatMessages.innerHTML = `
                <div class="flex items-start space-x-2">
                    <div class="bg-blue-100 text-blue-800 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="bg-white p-3 rounded-lg shadow-sm max-w-[80%]">
                        <p class="text-sm">👋 Hi! I'm your AI assistant. How can I help you today?</p>
                    </div>
                </div>
            `;
        }
    };

    /**
     * Toggle chat window (can be called from other scripts)
     */
    window.toggleChat = function() {
        chatToggle.click();
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChat);
    } else {
        initChat();
    }
})();
