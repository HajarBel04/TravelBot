document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const emailInput = document.getElementById('email-input');
    const submitBtn = document.getElementById('submit-btn');
    const loadingIndicator = document.getElementById('loading');

    submitBtn.addEventListener('click', sendMessage);
    emailInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const emailText = emailInput.value.trim();
        
        if (emailText === '') return;
        
        // Add user message to chat
        addMessage('user', emailText);
        
        // Clear input
        emailInput.value = '';
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        
        // Send to API
        processEmail(emailText);
    }

    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // If content is HTML (for formatted responses)
        if (type === 'assistant' && typeof content === 'object') {
            // Create a nicely formatted response for travel packages and proposal
            contentDiv.innerHTML = formatResponse(content);
        } else if (type === 'assistant' && content.includes('<')) {
            contentDiv.innerHTML = content;
        } else {
            const paragraph = document.createElement('p');
            paragraph.textContent = content;
            contentDiv.appendChild(paragraph);
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatResponse(responseData) {
        let html = '<div class="travel-response">';
        
        // Add extracted information if available
        if (responseData.extracted_info) {
            html += `<div class="extracted-info-section">
                <h3>Understanding Your Request</h3>
                <div class="extracted-info">`;
            
            const info = responseData.extracted_info;
            if (info.destination) html += `<p><strong>Destination:</strong> ${info.destination}</p>`;
            if (info.dates) html += `<p><strong>Travel Dates:</strong> ${info.dates}</p>`;
            if (info.duration) html += `<p><strong>Duration:</strong> ${info.duration}</p>`;
            if (info.budget) html += `<p><strong>Budget:</strong> ${info.budget}</p>`;
            if (info.travelers && info.travelers.count) html += `<p><strong>Travelers:</strong> ${info.travelers.count} ${info.travelers.type || 'people'}</p>`;
            if (info.interests && info.interests.length) {
                html += `<p><strong>Interests:</strong> ${info.interests.join(', ')}</p>`;
            }
            
            html += `</div>
            </div>`;
        }
        
        // Add the proposal
        if (responseData.proposal) {
            html += `<div class="proposal-section">
                <h3>Travel Proposal</h3>
                <div class="proposal-content">
                    ${responseData.proposal.replace(/\n/g, '<br>')}
                </div>
            </div>`;
        }
        
        // Add recommended packages if available
        if (responseData.packages && responseData.packages.length > 0) {
            html += '<div class="packages-section">';
            html += '<h3>Recommended Packages</h3>';
            
            responseData.packages.forEach(pkg => {
                html += `<div class="package-card">
                    <div class="package-title">${pkg.name}</div>
                    <div class="package-details">
                        <span class="package-detail">Location: ${pkg.location}</span>
                        <span class="package-detail">Duration: ${pkg.duration}</span>
                        <span class="package-detail">Price: $${pkg.price}</span>
                    </div>
                    <div class="package-description">${pkg.description}</div>
                    <div class="package-activities">`;
                
                pkg.activities.forEach(activity => {
                    html += `<span class="activity-tag">${activity}</span>`;
                });
                
                html += `</div>
                </div>`;
            });
            
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }

    async function processEmail(emailText) {
        try {
            const response = await fetch('/process-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: emailText })
            });
            
            if (!response.ok) {
                throw new Error('Error from server: ' + response.status);
            }
            
            const data = await response.json();
            
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            
            // Add assistant message to chat with the full response data
            addMessage('assistant', data);
            
        } catch (error) {
            console.error('Error:', error);
            loadingIndicator.style.display = 'none';
            addMessage('assistant', 'Sorry, there was an error processing your request. Please try again.');
        }
    }
});