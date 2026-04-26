/**
 * Multi-step Registration Logic
 */
function validateStep(current) {
    const step = document.getElementById('step-' + current);
    if (!step) return true;
    
    const inputs = Array.from(step.querySelectorAll('input, select')).filter(input => {
        if (input.type === 'file' || input.type === 'hidden' || input.type === 'button' || input.type === 'submit') return false;
        const isRequiredField = ['first_name', 'last_name', 'email', 'username', 'password', 'confirm_password', 'birthdate', 'gender', 'weight', 'height'].includes(input.name);
        return isRequiredField;
    });

    let isValid = true;
    let firstInvalid = null;

    inputs.forEach(input => {
        if (!input.value.trim() || !input.checkValidity()) {
            isValid = false;
            if (!firstInvalid) firstInvalid = input;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    if (!isValid && firstInvalid) {
        firstInvalid.focus();
        firstInvalid.reportValidity();
    }

    return isValid;
}

function goToStep(current, next) {
    if (next > current) {
        if (!validateStep(current)) return;
    }

    document.querySelectorAll('.step').forEach((s, i) => {
        s.classList.toggle('active', i + 1 === next);
    });
    
    // Scroll to the top of the card
    const card = document.querySelector('.register-card');
    if (card) {
        const scrollTarget = card.getBoundingClientRect().top + window.pageYOffset - 20;
        window.scrollTo({ top: scrollTarget, behavior: 'smooth' });
    }
}

function selectGoal(value, el) {
    document.querySelectorAll('.goal-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    const hidden = document.getElementById('fitness_goal_hidden');
    if (hidden) hidden.value = value;
}

function selectLevel(value, el) {
    document.querySelectorAll('.level-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    const hidden = document.getElementById('fitness_level_hidden');
    if (hidden) hidden.value = value;
}

function selectActivity(value, el) {
    document.querySelectorAll('.activity-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    const hidden = document.getElementById('activity_level_hidden');
    if (hidden) hidden.value = value;
}

function togglePassword(fieldId, btn) {
    const f = document.getElementById(fieldId);
    if (!f) return;
    const i = btn.querySelector('i');
    f.type = f.type === 'password' ? 'text' : 'password';
    i.classList.toggle('fa-eye'); 
    i.classList.toggle('fa-eye-slash');
}

function initPasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;

    passwordInput.addEventListener('input', function() {
        const pw = this.value;
        const checks = {
            length: pw.length >= 8,
            uppercase: /[A-Z]/.test(pw),
            lowercase: /[a-z]/.test(pw),
            number: /[0-9]/.test(pw),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(pw)
        };
        
        Object.keys(checks).forEach(function(k) {
            const li = document.querySelector('[data-requirement="' + k + '"]');
            if (li) {
                const ic = li.querySelector('i');
                li.classList.toggle('met', checks[k]);
                ic.className = checks[k] ? 'fas fa-check-circle' : 'fas fa-circle';
            }
        });

        const cnt = Object.values(checks).filter(Boolean).length;
        const sc = document.getElementById('passwordStrength');
        const st = document.getElementById('strengthText');
        if (sc && st) {
            sc.classList.remove('strength-weak','strength-medium','strength-strong');
            if (!pw) { st.textContent = '-'; }
            else if (cnt <= 2) { sc.classList.add('strength-weak'); st.textContent = 'Weak'; }
            else if (cnt <= 4) { sc.classList.add('strength-medium'); st.textContent = 'Medium'; }
            else { sc.classList.add('strength-strong'); st.textContent = 'Strong'; }
        }
    });
}

function initFileUpload() {
    const fileInput = document.getElementById('profile_image');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const filePreview = document.getElementById('filePreview');
    
    if (!fileUploadArea || !fileInput) return;

    ['dragenter','dragover','dragleave','drop'].forEach(function(e) {
        fileUploadArea.addEventListener(e, function(ev){ ev.preventDefault(); ev.stopPropagation(); });
    });

    ['dragenter','dragover'].forEach(function(e){
        fileUploadArea.addEventListener(e, function(){ fileUploadArea.classList.add('drag-over'); });
    });

    ['dragleave','drop'].forEach(function(e){
        fileUploadArea.addEventListener(e, function(){ fileUploadArea.classList.remove('drag-over'); });
    });

    fileUploadArea.addEventListener('drop', function(e){
        const files = e.dataTransfer.files;
        if (files.length){ 
            fileInput.files = files; 
            handleFile(files[0]); 
        }
    });

    fileInput.addEventListener('change', function(){ 
        if(this.files.length) handleFile(this.files[0]); 
    });
}

function handleFile(f) {
    if (!f.type.match('image.*')) return;
    const r = new FileReader();
    r.onload = function(e) {
        const previewImg = document.getElementById('previewImage');
        const previewName = document.getElementById('previewName');
        const previewSize = document.getElementById('previewSize');
        const filePreview = document.getElementById('filePreview');

        if (previewImg) previewImg.src = e.target.result;
        if (previewName) previewName.textContent = f.name;
        if (previewSize) previewSize.textContent = (f.size/1024).toFixed(1) + ' KB';
        if (filePreview) filePreview.classList.add('active');
    };
    r.readAsDataURL(f);
}

function removeFile() {
    const fileInput = document.getElementById('profile_image');
    const filePreview = document.getElementById('filePreview');
    if (fileInput) fileInput.value = ''; 
    if (filePreview) filePreview.classList.remove('active'); 
}

document.addEventListener('DOMContentLoaded', () => {
    initPasswordStrength();
    initFileUpload();

    const defaultCard = document.querySelector('.activity-card:nth-child(2)');
    if (defaultCard) selectActivity('Lightly Active', defaultCard);
});
