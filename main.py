import os
import logging
import random
import time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configurer le logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

# Charger le token depuis les variables d'environnement
TOKEN_TELE = os.getenv("TOKEN_TELE")

# États de la conversation
ASK_AGENT = 1  # État pour demander si l'utilisateur a rencontré l'agent

# Fonction de démarrage avec menu de boutons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["Santé", "Droits"],
        ["Menstruation", "Sécurité"],
        ["Signaler un danger"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        """
Bonjour et bienvenue ! Ce bot est là pour vous informer et vous soutenir sur des sujets essentiels comme votre santé, vos droits,
et votre bien-être. Vous y trouverez des conseils pratiques, des informations précieuses, et des options pour défendre vos droits.
Un autre point important : vous avez la possibilité de signaler en toute sécurité tout danger concernant vous-même ou vos proches.
Veuillez choisir une option ci-dessous pour commencer.
        """,
        reply_markup=reply_markup
    )

# Fonction pour poser la question si l'utilisateur a rencontré un agent
async def ask_user_about_agent(update: Update):
    keyboard = [["Oui", "Non"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        "Avez-vous rencontré l'agent ? (Répondez par 'Oui' ou 'Non')",
        reply_markup=reply_markup
    )

    # Retourner ASK_AGENT pour indiquer l'étape suivante
    return ASK_AGENT

# Fonction pour gérer la réponse de l'utilisateur ("Oui" ou "Non")
async def handle_agent_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower()
    print(f"Réponse de l'utilisateur : {user_input}")  # Affichage pour le débogage

    if user_input == "oui":
        await update.message.reply_text("Merci de nous avoir informé ! L'agent que vous avez rencontré est le meilleur pour vous aider. Restez clair avec lui, nous croyons en lui.")
        return ConversationHandler.END  # Fin de la conversation
    elif user_input == "non":
        await update.message.reply_text("Ne perdez pas patience, nous continuons à chercher un agent pour vous.")
        return ConversationHandler.END  # Fin de la conversation
    else:
        await update.message.reply_text("Je n'ai pas compris votre réponse. Veuillez répondre par 'Oui' ou 'Non'.")
        return ASK_AGENT  # Retour à la question initiale

# Fonction pour gérer les autres messages du menu (Santé, Droits, etc.)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    print(f"Réponse de l'utilisateur : {user_input}")  # Affichage pour le débogage

    if user_input == "Santé":
        await sante(update, context)
    elif user_input == "Droits":
        await droits(update, context)
    elif user_input == "Menstruation":
        await menstruation(update, context)
    elif user_input == "Sécurité":
        await securite(update, context)
    elif user_input == "Signaler un danger":
        await update.message.reply_text(
            "Veuillez entrer votre adresse complète pour signaler un danger, en utilisant le format :\n"
            "/signaler [adresse complète]\n"
            "Exemple : /signaler 123 Rue des Lilas, Paris"
        )
    else:
        await update.message.reply_text("Je n'ai pas compris votre demande. Veuillez sélectionner une option du menu.")

# Gestion des autres fonctions comme sante, droits, etc.
async def sante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voici des informations sur la santé...")

async def droits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voici des informations sur les droits...")

async def menstruation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voici des informations sur les menstruations...")

async def securite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voici des informations sur la sécurité...")

# Fonction de signalement
async def signaler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    adresse_complet = update.message.text.replace("/signaler ", "").strip()

    if not adresse_complet:
        await update.message.reply_text(f"""
Ooh {user.username},
Vous n'avez pas fourni d'adresse complète. Veuillez utiliser la commande avec le format :
/signaler [adresse complète]
Exemple : /signaler 123 Rue des Lilas, Paris
        """)
        return ConversationHandler.END

    if not valid_address_format(adresse_complet):
        await update.message.reply_text(f"""
{user.username}, l'adresse que vous avez entrée semble incorrecte.
Veuillez réessayer avec un format valide. Exemple : /signaler 123 Rue des Lilas, Paris
        """)
        return ConversationHandler.END

    await update.message.reply_text(f"""
Salut {user.username},
Nous vérifions votre demande. Un agent va être trouvé pour vous dans quelques minutes.
Veuillez patienter pendant que nous recherchons l'agent le plus proche de votre adresse.
    """)
    await search_for_agent(update, adresse_complet)

# Fonction de validation de l'adresse
def valid_address_format(address: str):
    return len(address.split()) >= 2

# Fonction pour rechercher un agent
async def search_for_agent(update: Update, adresse_complet: str):
    user = update.message.from_user
    agent_found = False

    for attempt in range(5):
        time.sleep(2)

        agent_found = random.choice([True, False])

        if agent_found:
            await update.message.reply_text(f"""
{user.username}, un agent a été trouvé près de votre adresse !
Il est en route et arrivera dans quelques minutes. Merci de patienter.
            """)
            break
        else:
            await update.message.reply_text(f"""
Aucun agent trouvé près de votre adresse pour le moment.
Nous continuons à chercher, veuillez patienter...
                """)
            
    # Demander confirmation à l'utilisateur
    return await ask_user_about_agent(update)

# Définir le handler de conversation
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("signaler", signaler)],
    states={
        ASK_AGENT: [MessageHandler(filters.Regex("^(Oui|Non)$"), handle_agent_response)],
    },
    fallbacks=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
)

# Initialiser l'application et ajouter les handlers
if __name__ == "__main__":
    application = Application.builder().token(TOKEN_TELE).build()

    # Ajouter les handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conversation_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Lancer le bot
    application.run_polling()
