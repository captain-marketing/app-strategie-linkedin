import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from tasks import generate_strategy_task

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Affiche la page d'accueil avec le formulaire."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    Cette route reçoit les données au format JSON,
    crée une tâche pour le worker Celery et répond immédiatement.
    """
    # On récupère les données JSON envoyées par le script
    form_data = request.get_json()

    # On lance la tâche en arrière-plan avec .delay()
    generate_strategy_task.delay(form_data)

    # On répond immédiatement au navigateur avec un message de succès
    return jsonify({
        "status": "success",
        "message": "Parfait ! Ta stratégie est en cours de création, surveille tes e-mails."
    })

if __name__ == '__main__':
    app.run(debug=True)