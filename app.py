import os
import google.generativeai as genai
from flask import Flask, render_template, request
from markupsafe import Markup
from dotenv import load_dotenv
import markdown2

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Configurer l'API Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Clé d'API Gemini non trouvée. Veuillez la définir dans le fichier .env")
genai.configure(api_key=api_key)

# Initialiser l'application Flask
app = Flask(__name__)

# Modèle pour la génération de texte
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    """Affiche la page d'accueil avec le formulaire."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Génère la stratégie LinkedIn via l'API Gemini."""
    try:
        # Lire le modèle de prompt depuis le fichier
        with open('prompt_template.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        # Formatter le prompt avec les données du formulaire
        final_prompt = prompt_template.format(
            q1_produit=request.form['produit'],
            q2_resultat=request.form['resultat'],
            q3_client=request.form['client'],
            q4_outils=request.form['outils'],
            q5_objectifs=request.form['objectifs'],
            q6_mesures=request.form['mesures'],
            q7_contraintes=request.form['contraintes'],
            q8_experience=request.form['experience']
        )

        # Appeler l'API Gemini
        response = model.generate_content(final_prompt)
        
        # Convertir la réponse Markdown en HTML, en activant l'extension pour les tableaux
        html_content = markdown2.markdown(
            response.text, 
            extras=["tables", "fenced-code-blocks", "break-on-newline"]
        )

        # Rendre la page de résultats avec le contenu généré
        return render_template('results.html', content=Markup(html_content))

    except Exception as e:
        # Gérer les erreurs (ex: clé API invalide, erreur de l'API)
        print(f"Une erreur est survenue : {e}")
        error_message = f"Désolé, une erreur est survenue lors de la génération de la stratégie. Détails : {e}"
        return render_template('results.html', content=Markup(f"<p style='color:red;'>{error_message}</p>"))

if __name__ == '__main__':
    app.run(debug=True)