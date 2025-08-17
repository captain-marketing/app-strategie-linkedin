document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('strategy-form');
    const spinner = document.getElementById('loading-spinner');
    const formResponseContainer = document.getElementById('form-response');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            spinner.classList.remove('hidden');
            form.classList.add('hidden');

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

            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                // --- DÉBUT DE LA MODIFICATION ---
                // On vérifie si la réponse du serveur est un succès (status 2xx)
                if (response.ok) {
                    return response.json(); // Si oui, on continue normalement
                }
                // Si non, on gère l'erreur
                if (response.status === 429) {
                    // Erreur spécifique pour la limitation de débit
                    throw new Error('Too Many Requests');
                }
                // Autres erreurs serveur (500, etc.)
                throw new Error('Server Error');
                // --- FIN DE LA MODIFICATION ---
            })
            .then(data => {
                setTimeout(() => {
                    spinner.classList.add('hidden');
                    if (data.status === 'success') {
                        formResponseContainer.innerHTML = `<p class="success-message">✅ Parfait ! Ta stratégie est en cours de création, surveille tes e-mails (pense à vérifier tes Spams, on ne sait jamais !).</p>`;
                    } else {
                        formResponseContainer.innerHTML = `<p class="error-message">❌ Une erreur est survenue.</p>`;
                    }
                }, 4000);
            })
            .catch(error => {
                spinner.classList.add('hidden');
                // On affiche un message personnalisé en fonction de l'erreur
                if (error.message === 'Too Many Requests') {
                    formResponseContainer.innerHTML = `<p class="error-message">⏳ Vous avez fait trop de demandes. Veuillez réessayer dans une heure.</p>`;
                } else {
                    formResponseContainer.innerHTML = `<p class="error-message">❌ Erreur de connexion au serveur.</p>`;
                }
                console.error('Error:', error);
            });
        });
    }
});