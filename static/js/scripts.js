document.addEventListener('DOMContentLoaded', () => {
    const contactButton = document.getElementById('contact-btn');

    contactButton.addEventListener('click', (e) => {
        e.preventDefault();
        alert('Redirecting to the Contact Us page!');
        window.location.href = contactButton.getAttribute('href');
    });
});
