/**
 * User Settings Interactions
 */

let soreMuscles = {};

function switchTab(tabId, element) {
    // Update active class on nav items
    document.querySelectorAll('.settings-tab-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to clicked item
    element.classList.add('active');
    
    // Hide all sections
    document.querySelectorAll('.settings-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const target = document.getElementById(tabId);
    if (target) {
        target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function initRecovery() {
    const input = document.getElementById('sore-muscles-input');
    if (input && input.value) {
        try {
            soreMuscles = JSON.parse(input.value);
            Object.keys(soreMuscles).forEach(muscle => {
                const el = document.querySelector(`.muscle-tag[data-muscle="${muscle}"]`);
                if (el) {
                    el.classList.add('active');
                    el.dataset.intensity = soreMuscles[muscle];
                    updateDots(el, soreMuscles[muscle]);
                }
            });
            generateRecoveryPlan();
        } catch (e) {
            console.error("Error parsing sore muscles:", e);
            soreMuscles = {};
        }
    }
}

function toggleMuscle(el, muscle) {
    const intensities = ['none', 'mild', 'moderate', 'severe'];
    let currentIdx = intensities.indexOf(el.dataset.intensity || 'none');
    let nextIdx = (currentIdx + 1) % intensities.length;
    let nextIntensity = intensities[nextIdx];

    el.dataset.intensity = nextIntensity;
    
    if (nextIntensity === 'none') {
        el.classList.remove('active');
        delete soreMuscles[muscle];
    } else {
        el.classList.add('active');
        soreMuscles[muscle] = nextIntensity;
    }

    updateDots(el, nextIntensity);
    const input = document.getElementById('sore-muscles-input');
    if (input) input.value = JSON.stringify(soreMuscles);
    generateRecoveryPlan();
}

function updateDots(el, intensity) {
    const dots = el.querySelectorAll('.dot');
    const levels = { 'none': 0, 'mild': 1, 'moderate': 2, 'severe': 3 };
    const activeCount = levels[intensity];
    
    dots.forEach((dot, i) => {
        if (i < activeCount) {
            dot.style.background = getIntensityColor(intensity);
        } else {
            dot.style.background = '#e9ecef';
        }
    });
}

function getIntensityColor(intensity) {
    if (intensity === 'mild') return '#fcc419';
    if (intensity === 'moderate') return '#fd7e14';
    if (intensity === 'severe') return '#fa5252';
    return '#e9ecef';
}

function clearSoreness() {
    document.querySelectorAll('.muscle-tag').forEach(el => {
        el.classList.remove('active');
        el.dataset.intensity = 'none';
        updateDots(el, 'none');
    });
    soreMuscles = {};
    const input = document.getElementById('sore-muscles-input');
    if (input) input.value = '{}';
    generateRecoveryPlan();
}

function generateRecoveryPlan() {
    const box = document.getElementById('recovery-plan');
    const content = document.getElementById('recovery-content');
    if (!box || !content) return;

    const muscles = Object.keys(soreMuscles);

    if (muscles.length === 0) {
        box.style.display = 'none';
        return;
    }

    box.style.display = 'block';
    let html = '<ul class="list-unstyled">';
    
    muscles.forEach(m => {
        const intensity = soreMuscles[m];
        let advice = "";
        if (intensity === 'mild') advice = "Light stretching and dynamic warm-up. Continue normal training.";
        if (intensity === 'moderate') advice = "Reduce volume by 50%. Focus on foam rolling and hydration.";
        if (intensity === 'severe') advice = "Complete rest or active recovery (walking/swimming). Avoid direct loading.";
        
        html += `<li class="mb-2"><strong>${m} (${intensity}):</strong> ${advice}</li>`;
    });
    
    html += '</ul><p class="mt-3 small text-muted"><i class="fas fa-info-circle"></i> This plan is dynamically adjusted based on your muscle soreness levels.</p>';
    content.innerHTML = html;
}

function togglePassword(element) {
    const input = element.parentElement.previousElementSibling;
    if (input.type === "password") {
        input.type = "text";
        element.classList.remove("fa-eye");
        element.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        element.classList.remove("fa-eye-slash");
        element.classList.add("fa-eye");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initRecovery();
    
    // Handle App Connections (AJAX)
    document.querySelectorAll('.integration-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('.toggle-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Processing...';
            btn.disabled = true;
            
            const url = this.getAttribute('action');
            const formData = new FormData(this);
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                btn.disabled = false;
                if (data.success) {
                    location.reload(); 
                } else {
                    btn.innerHTML = originalText;
                    alert('Something went wrong.');
                }
            })
            .catch(err => {
                btn.disabled = false;
                btn.innerHTML = originalText;
                console.error('Error:', err);
            });
        });
    });
});
