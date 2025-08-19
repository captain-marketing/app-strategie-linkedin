import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
CORS(app)

# Initialiser Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    storage_options={"socket_connect_timeout": 3},
    strategy="fixed-window",
)

# Assure-toi que 'request' est bien importé en haut du fichier
# from flask import Flask, render_template, request, jsonify

@app.route('/')
def index():
    """Affiche la page d'accueil et pré-remplit l'e-mail si présent dans l'URL."""
    # On récupère la valeur du paramètre 'email' dans l'URL
    user_email = request.args.get('email', '')
    return render_template('index.html', user_email=user_email)

@app.route('/generate', methods=['POST'])
@limiter.limit("5 per hour")
def generate():
    """
    Cette route est maintenant protégée contre les abus.
    """
    # --- LA MODIFICATION EST ICI ---
    # On importe la tâche uniquement au moment où on en a besoin.
    from tasks import generate_strategy_task
    
    form_data = request.get_json()
    generate_strategy_task.delay(form_data)
    return jsonify({
        "status": "success",
        "message": "Parfait ! Ta stratégie est en cours de création, surveille tes e-mails."
    })

if __name__ == '__main__':
    app.run(debug=True)