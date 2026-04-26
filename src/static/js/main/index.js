/**
 * Home Page Interactions
 */
document.addEventListener('DOMContentLoaded', () => {
    initQuickView();
    initFAQ();
});

function initQuickView() {
    document.querySelectorAll('.quick-view-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const programId = button.dataset.programId;
            const modal = document.getElementById('quickViewModal');
            const container = document.getElementById('exercisesContainer');
            const title = document.getElementById('modalTitle');

            if (!modal || !container || !title) return;

            // Reset and show modal
            container.innerHTML = `
                <div class="premium-loader">
                    <div class="spinner"></div>
                    <p>Loading curriculum data...</p>
                </div>
            `;
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('active'), 10);
            document.body.style.overflow = 'hidden'; 
            
            try {
                const response = await fetch(`/api/program/${programId}`);
                const data = await response.json();
                
                title.innerText = data.title;
                
                container.innerHTML = data.exercises.map((ex, index) => `
                    <div class="premium-mini-card" style="animation-delay: ${index * 0.08}s">
                        <div class="card-icon-wrapper">
                            <i class="fas ${ex.icon}"></i>
                        </div>
                        <div class="card-info-compact">
                            <h4>${ex.name}</h4>
                            <p class="ex-desc">${ex.desc}</p>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                container.innerHTML = '<div class="no-data-msg">Error loading curriculum data. Please try again.</div>';
            }
        });
    });

    const closeModalBtn = document.querySelector('.close-modal-btn');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    window.addEventListener('click', (e) => { 
        if (e.target.classList.contains('modal-overlay')) closeModal(); 
    });
}

function closeModal() {
    const modal = document.getElementById('quickViewModal');
    if (!modal) return;
    modal.classList.remove('active');
    setTimeout(() => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }, 300);
}

function initFAQ() {
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', () => {
            const item = question.parentElement;
            
            // Close others
            document.querySelectorAll('.faq-item').forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current
            item.classList.toggle('active');
        });
    });
}
