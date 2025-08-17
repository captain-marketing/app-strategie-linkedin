import os
import smtplib
from email.message import EmailMessage
import markdown2
import google.generativeai as genai
from celery import Celery
from dotenv import load_dotenv
import traceback

# Load environment variables for the worker
load_dotenv()

# Configuration for sending email
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_strategy_email(recipient_email, strategy_markdown):
    """Prepares and sends the email with the strategy (WITHOUT PDF)."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("ERROR: EMAIL_ADDRESS or EMAIL_APP_PASSWORD not configured.")
        return

    # Convert Markdown to HTML for the email body
    strategy_html = markdown2.markdown(
        strategy_markdown,
        extras=["tables", "fenced-code-blocks"]
    )

    full_html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
                h2 {{ border-bottom: 2px solid #0077b5; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h1>Ta Stratégie LinkedIn Personnalisée</h1>
            <p>Merci d'avoir utilisé notre générateur. Voici le plan d'action créé par l'IA :</p>
            <hr>
            {strategy_html}
            <hr>
            <p>Cordialement,<br>L'équipe</p>
        </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = "🚀 Ta stratégie de contenu LinkedIn"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.add_alternative(full_html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
            print(f"E-mail de stratégie (sans PDF) envoyé avec succès à {recipient_email}")

    except Exception as e:
        print("ERREUR détaillée lors de l'envoi de l'e-mail :")
        print(traceback.format_exc())

# --- Celery Task ---
celery = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("ATTENTION: Clé d'API Gemini non trouvée pour le worker Celery.")

@celery.task
def generate_strategy_task(form_data):
    """
    Asynchronous task that calls the Gemini API and sends the result via email.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    recipient = form_data.get('email', None)

    if not recipient:
        print("ERROR: No recipient email to send the result to.")
        return "Failure: missing email."

    try:
        with open('prompt_template.txt', 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        final_prompt = prompt_template.format(**form_data)
        response = model.generate_content(final_prompt)

        send_strategy_email(recipient, response.text)

        return "Task completed and email sent."

    except Exception as e:
        print("Detailed ERROR in generate_strategy_task:")
        print(traceback.format_exc())
        return f"Task Failure: {e}"