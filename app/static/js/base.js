// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelectorAll('.flash-message').forEach(function (el) {
            el.classList.remove('show');
            setTimeout(() => el.remove(), 150);
        });
    }, 5000);
});
