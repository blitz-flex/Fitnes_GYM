// Flash messages functionality
function closeFlashMessage(button) {
    const message = button.closest('.flash-message');
    message.style.animation = 'slideOut 0.4s ease-in-out forwards';
    setTimeout(() => {
        message.remove();
        // If no more messages, hide the container
        const container = document.querySelector('.flash-messages');
        if (container && container.children.length === 0) {
            container.style.display = 'none';
        }
    }, 400);
}

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach((message, index) => {
        // Add slight delay for multiple messages
        const delay = index * 200;

        // Auto-hide after 5 seconds + delay
        setTimeout(() => {
            const closeBtn = message.querySelector('.flash-close');
            if (closeBtn && message.parentNode) {
                closeFlashMessage(closeBtn);
            }
        }, 5000 + delay);

        // Pause auto-hide on hover
        let timeoutId;
        const autoHide = () => {
            timeoutId = setTimeout(() => {
                const closeBtn = message.querySelector('.flash-close');
                if (closeBtn && message.parentNode) {
                    closeFlashMessage(closeBtn);
                }
            }, 5000 + delay);
        };

        message.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
            const progressBar = message.querySelector('.flash-progress');
            if (progressBar) {
                progressBar.style.animationPlayState = 'paused';
            }
        });

        message.addEventListener('mouseleave', () => {
            const progressBar = message.querySelector('.flash-progress');
            if (progressBar) {
                progressBar.style.animationPlayState = 'running';
            }
            autoHide();
        });
    });

    // Add sound effect for messages (optional)
    if (flashMessages.length > 0) {
        playNotificationSound();
    }
});

// Optional: Add notification sound
function playNotificationSound() {
    // Create audio context for notification sound
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(600, audioContext.currentTime + 0.1);

        gainNode.gain.setValueAtTime(0, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.1);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    } catch (e) {
        // Silently fail if audio context is not supported
    }
}

// Add dynamic message creation function
function showFlashMessage(message, category = 'info') {
    const container = document.querySelector('.flash-messages') || createFlashContainer();

    const flashDiv = document.createElement('div');
    flashDiv.className = `flash-message ${category}`;
    flashDiv.setAttribute('data-category', category);

    const iconMap = {
        'error': 'fa-exclamation-triangle',
        'success': 'fa-check-circle',
        'warning': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    };

    flashDiv.innerHTML = `
        <div class="flash-icon">
            <i class="fas ${iconMap[category] || 'fa-bell'}"></i>
        </div>
        <div class="flash-content">${message}</div>
        <button class="flash-close" onclick="closeFlashMessage(this)" title="დახურვა">
            <i class="fas fa-times"></i>
        </button>
        <div class="flash-progress"></div>
    `;

    container.appendChild(flashDiv);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        const closeBtn = flashDiv.querySelector('.flash-close');
        if (closeBtn && flashDiv.parentNode) {
            closeFlashMessage(closeBtn);
        }
    }, 5000);

    playNotificationSound();
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    const form = document.querySelector('.register-form');
    form.parentNode.insertBefore(container, form);
    return container;
}
