document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('strategy-form');
    const spinner = document.getElementById('loading-spinner');
    const formResponseContainer = document.getElementById('form-response');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            spinner.classList.remove('hidden');

            // 1. On construit manuellement notre objet de données. C'est plus fiable.
            const formData = {
                email: document.getElementById('email').value,
                produit: document.getElementById('produit').value,
                resultat: document.getElementById('resultat').value,
                client: document.getElementById('client').value,
                outils: document.getElementById('outils').value,
                objectifs: document.getElementById('objectifs').value,
                mesures: document.getElementById('mesures').value,
                contraintes: document.getElementById('contraintes').value,
                experience: document.getElementById('experience').value,
            };

            // 2. On envoie les données en format JSON.
            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // On précise qu'on envoie du JSON
                },
                body: JSON.stringify(formData) // On convertit notre objet en chaîne de caractères JSON
            })
            .then(response => response.json())
            .then(data => {
                spinner.classList.add('hidden');
                form.classList.add('hidden');

                if (data.status === 'success') {
                    formResponseContainer.innerHTML = `<p class="success-message">✅ Parfait ! Ta stratégie est en cours de création, surveille tes e-mails (pense à vérifier tes Spams, on ne sait jamais !).</p>`;
                } else {
                    formResponseContainer.innerHTML = `<p class="error-message">❌ Une erreur est survenue.</p>`;
                }
            })
            .catch(error => {
                spinner.classList.add('hidden');
                formResponseContainer.innerHTML = `<p class="error-message">❌ Erreur de connexion au serveur.</p>`;
                console.error('Error:', error);
            });
        });
    }
});