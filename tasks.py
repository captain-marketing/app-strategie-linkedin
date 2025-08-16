import os
import smtplib
from email.message import EmailMessage
import markdown2
import google.generativeai as genai
from celery import Celery
from dotenv import load_dotenv
import traceback  # <-- ASSURE-TOI QUE CET IMPORT EST PRÉSENT

# Charger les variables d'environnement pour le worker !
load_dotenv()

# --- Configuration pour l'envoi d'e-mail ---
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_strategy_email(recipient_email, strategy_markdown):
    """Prépare et envoie l'e-mail avec la stratégie."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("ERREUR: EMAIL_ADDRESS ou EMAIL_APP_PASSWORD non configuré.")
        return

    strategy_html = markdown2.markdown(
        strategy_markdown,
        extras=["tables", "fenced-code-blocks"]
    )

    msg = EmailMessage()
    # Objet de l'e-mail mis à jour
    msg['Subject'] = "🚀 Ta stratégie de contenu LinkedIn"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    msg.set_content("Veuillez activer l'affichage HTML pour voir votre stratégie.")
    
    # Corps de l'e-mail mis à jour avec le tutoiement
    msg.add_alternative(f"""
    <html>
        <head>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; }}
                h2 {{ border-bottom: 2px solid #0077b5; padding-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Ta Stratégie LinkedIn Personnalisée</h1>
            <p>Bonjour,</p>
            <p>Merci d'avoir utilisé notre générateur. Voici le plan d'action sur mesure créé par l'IA, basé sur les informations que tu as fournies :</p>
            <hr>
            {strategy_html}
            <hr>
            <p>Nous espérons que cette stratégie t'aidera à atteindre tes objectifs. N'hésite pas à nous contacter pour toute question.</p>
            <p>Cordialement,<br>L'équipe</p>
        </body>
    </html>
    """, subtype='html')

    try:
        email_bytes = msg.as_bytes()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.sendmail(SENDER_EMAIL, recipient_email, email_bytes)
            print(f"E-mail de stratégie envoyé avec succès à {recipient_email}")
            
    except Exception as e:
        import traceback
        print("ERREUR détaillée lors de l'envoi de l'e-mail :")
        print(traceback.format_exc())


# --- Tâche Celery ---
# Récupérer l'URL du broker depuis les variables d'environnement
# Utilise l'URL de Koyeb si elle existe, sinon localhost pour le dev local
redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

celery = Celery(
    __name__,
    broker=redis_url,
    backend=redis_url
)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("ATTENTION: Clé d'API Gemini non trouvée pour le worker Celery.")

@celery.task
def generate_strategy_task(form_data):
    """
    Tâche asynchrone qui appelle l'API Gemini et envoie le résultat par e-mail.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    recipient = form_data.get('email', None)

    if not recipient:
        print("ERREUR: Pas d'e-mail de destinataire pour envoyer le résultat.")
        return "Échec : e-mail manquant."

    try:
        with open('prompt_template.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        final_prompt = prompt_template.format(**form_data)
        response = model.generate_content(final_prompt)
        
        # On passe le texte brut, sans nettoyage, pour que l'erreur se produise si elle doit se produire.
        send_strategy_email(recipient, response.text)
        
        return "Tâche complétée et e-mail envoyé."
        
    except Exception as e:
        print(f"ERREUR lors de l'exécution de la tâche : {e}")
        return f"Échec de la tâche : {e}"