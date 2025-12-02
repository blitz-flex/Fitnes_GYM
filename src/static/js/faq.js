    function toggleFAQ(element) {
        const answer = element.nextElementSibling;
        const icon = element.querySelector('.faq-icon');

        // Close all other FAQ items
        document.querySelectorAll('.faq-question').forEach(q => {
            if(q !== element) {
                q.classList.remove('active');
                q.nextElementSibling.classList.remove('active');
                q.querySelector('.faq-icon').textContent = '+';
            }
        });

        // Toggle current item
        element.classList.toggle('active');
        answer.classList.toggle('active');

        if(element.classList.contains('active')) {
            icon.textContent = '×';
        } else {
            icon.textContent = '+';
        }
    }