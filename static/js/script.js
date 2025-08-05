document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('strategy-form');
    const spinner = document.getElementById('loading-spinner');

    if (form) {
        form.addEventListener('submit', function() {
            // Vérifie la validité de base du formulaire avant d'afficher le spinner
            if (form.checkValidity()) {
                spinner.classList.remove('hidden');
            }
        });
    }
});