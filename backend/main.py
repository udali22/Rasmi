from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
import json
import re
import random

app = FastAPI(
    title="Rasmi API",
    description="API de génération d'emails académiques formels (Version Améliorée)"
)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Schemas
# =========================
class EmailRequest(BaseModel):
    intention: str
    niveau_formalite: Literal["faible", "moyen", "élevé"]

class EmailResponse(BaseModel):
    objet: str
    corps: str

# =========================
# 0️⃣ Nettoyage et validation de l'intention
# =========================
def nettoyer_intention(intention: str) -> str:
    """Nettoie et normalise l'intention utilisateur"""
    
    # Suppression des caractères parasites
    intention = re.sub(r'\s+', ' ', intention.strip())
    
    # Correction d'abréviations et fautes courantes
    corrections = {
        r'\bsvp\b': "s'il vous plaît",
        r'\bmrc\b': 'merci',
        r'\bprof\b': 'professeur',
        r'\brdv\b': 'rendez-vous',
        r'\basap\b': 'dès que possible',
        r'\bpv\b': 'procès-verbal',
        r'\bcv\b': 'curriculum vitae',
        r'\bjedi\b': 'jeudi',
        r'\bétre\b': 'être',
        r'\betre\b': 'être',
        r'\bètre\b': 'être',
        r'\bvai\b': 'vais',
        r'\ba cause de\b': 'en raison de'
    }
    
    for pattern, remplacement in corrections.items():
        intention = re.sub(pattern, remplacement, intention, flags=re.IGNORECASE)
    
    return intention.strip()

def detecter_ton_inapproprie(intention: str) -> tuple:
    """Détecte si le ton est inapproprié pour un email académique"""
    
    patterns_inappropries = [
        (r'\b(yo|salut|coucou|wesh|hey)\b', "Formulation trop informelle détectée"),
        (r'[!]{2,}', "Trop de points d'exclamation"),
        (r'[A-Z]{5,}', "Majuscules excessives"),
        (r'\b(vite|urgent|immédiatement)\b.*[!]', "Ton trop pressant")
    ]
    
    for pattern, message in patterns_inappropries:
        if re.search(pattern, intention, re.IGNORECASE):
            return True, message
    
    return False, ""

# =========================
# 1️⃣ Détection de l'action (Optimisée)
# =========================
def detect_action(intention: str) -> str:
    text = intention.lower()
    
    categories = {
        "demande_rendez_vous": [r"rdv", r"rendez-vous", r"rencontrer", r"créneau", r"disponibilité", r"soutenance", r"pfe"],
        "demande_prolongation": [r"prolongation", r"délai", r"retarder", r"soumettre", r"plus tard", r"rapport", r"décaler", r"reporter"],
        "demande_document": [r"document", r"attestation", r"certificat", r"papier", r"relevé"],
        "excuse_absence": [r"absence", r"absent", r"manquer", r"cours", r"excuser", r"justifier"],
        "relance": [r"relance", r"réponse", r"suite à", r"nouvelles", r"retour"],
        "remerciement": [r"merci", r"remercier", r"remerciement", r"gratitude", r"reconnaissance"],
        "demande_information": [r"information", r"renseignement", r"question", r"précision", r"comprendre", r"savoir"]
    }

    for cat, patterns in categories.items():
        if any(re.search(pattern, text) for pattern in patterns):
            return cat
    return "autre"

# =========================
# 2️⃣ Extraction contextuelle enrichie
# =========================
def extraire_contexte(intention: str) -> dict:
    """Extrait les entités clés de l'intention"""
    i = intention.lower()
    
    contexte = {
        "sujet": None,
        "date": None,
        "personne": None,
        "raison": None,
        "futur": False
    }
    
    # Détection futur
    if re.search(r"serai|vais être|prochain|demain|semaine prochaine", i):
        contexte["futur"] = True
    
    # Extraction du sujet académique
    sujets = [
        (r"soutenance.{0,10}pfe", "la soutenance de mon projet de fin d'études"),
        (r"rapport.{0,10}stage", "mon rapport de stage"),
        (r"rapport", "mon rapport académique"),
        (r"stage", "mon stage"),
        (r"projet.{0,10}fin.{0,10}études", "mon projet de fin d'études"),
        (r"pfe", "mon projet de fin d'études"),
        (r"pfa", "mon projet de fin d'année"),
        (r"note.{0,15}ds\b", "la note de Devoir Surveillé"),
        (r"note.{0,15}td\b", "la note de TD"),
        (r"note.{0,15}tp\b", "la note de TP"),
        (r"note.{0,15}exam", "la note d'examen"),
        (r"td\b", "le TD"),
        (r"ds\b", "le Devoir Surveillé"),
        (r"tp\b", "le TP"),
        (r"examen", "l'examen"),
        (r"exam", "l'examen"),
        (r"cours\s+de\s+(\w+)", lambda m: f"le cours de {m.group(1)}"),
        (r"cours", "le cours"),
        (r"mémoire", "mon mémoire"),
        (r"thèse", "ma thèse")
    ]
    
    for pattern, sujet in sujets:
        match = re.search(pattern, i)
        if match:
            if callable(sujet):
                contexte["sujet"] = sujet(match)
            else:
                contexte["sujet"] = sujet
            break
    
    if not contexte["sujet"]:
        contexte["sujet"] = "le sujet mentionné"
    
    # Extraction de dates
    date_patterns = [
        (r"(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)", lambda m: m.group(1)),
        (r"((?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)(?:\s+(?:prochain|dernier))?)", lambda m: m.group(1)),
        (r"(demain|aujourd'hui|cette semaine|semaine prochaine)", lambda m: m.group(1))
    ]
    
    for pattern, formatter in date_patterns:
        match = re.search(pattern, i)
        if match:
            contexte["date"] = formatter(match)
            break
    
    # Extraction de la raison (pour absences/prolongations)
    raisons = {
        r"maladie|malade|santé|médical": "pour des raisons de santé (maladie)",
        r"urgence.{0,10}familiale": "pour une urgence familiale",
        r"problème.{0,10}(transport|bus|métro|car)": "en raison d'un problème de transport imprévu",
        r"problème.{0,10}technique": "en raison de difficultés techniques",
        r"charge.{0,10}travail": "en raison d'une charge de travail importante",
        r"problème.{0,10}personnel": "pour des raisons personnelles",
        r"imprévu": "en raison d'un imprévu",
        r"révision|réviser|préparer.{0,10}examen": "pour la préparation d'un examen imminent"
    }
    
    for pattern, raison in raisons.items():
        if re.search(pattern, i):
            contexte["raison"] = raison
            break
    
    return contexte

# =========================
# 3️⃣ Variations linguistiques
# =========================
def varier_formulation(action: str, niveau_formalite: str) -> dict:
    """Retourne des variantes de formulations"""
    
    variantes_introduction = {
        "faible": [
            "Je me permets de vous contacter pour",
            "Je vous écris afin de",
            "Je souhaiterais"
        ],
        "moyen": [
            "Je me permets de vous solliciter pour",
            "Je vous contacte dans le but de",
            "Je me tourne vers vous afin de"
        ],
        "élevé": [
            "Je me permets de solliciter votre bienveillance pour",
            "J'ai l'honneur de vous solliciter afin de",
            "Je prends la liberté de vous écrire pour"
        ]
    }
    
    return {
        "intro": random.choice(variantes_introduction.get(niveau_formalite, variantes_introduction["moyen"]))
    }

# =========================
# 4️⃣ Génération de l'objet personnalisé
# =========================
def generer_objet_personnalise(action: str, contexte: dict) -> str:
    """Génère un objet d'email personnalisé selon le contexte"""
    
    objets_base = {
        "demande_rendez_vous": "Demande de rendez-vous",
        "demande_prolongation": "Demande de prolongation de délai",
        "demande_information": "Demande d'information",
        "demande_document": "Demande de document",
        "excuse_absence": "Justification d'absence",
        "relance": "Suivi de mon précédent message",
        "remerciement": "Remerciements",
        "autre": "Contact étudiant"
    }
    
    objet = objets_base.get(action, "Contact étudiant")
    
    # Personnalisation selon le sujet
    if contexte["sujet"] and contexte["sujet"] != "le sujet mentionné":
        if action == "demande_rendez_vous":
            objet = f"Demande de rendez-vous - {contexte['sujet']}"
        elif action == "excuse_absence" and contexte["date"]:
            objet = f"Justification d'absence - {contexte['date']}"
        elif action == "demande_prolongation":
            objet = f"Demande de prolongation - {contexte['sujet']}"
    
    return objet

# =========================
# 5️⃣ Construction du corps enrichi
# =========================
def construire_corps_email(action: str, contexte: dict, niveau_formalite: str, variantes: dict) -> str:
    """Génère le corps de l'email avec le contexte enrichi"""
    
    templates_enrichis = {
        "demande_rendez_vous": lambda c, v: (
            f"{v['intro']} convenir d'un rendez-vous "
            f"afin de discuter de {c['sujet']}."
            + (f" Je serais disponible {c['date']}." if c['date'] else "")
            + " Pourriez-vous m'indiquer vos disponibilités ?"
        ),
        
        "demande_prolongation": lambda c, v: (
            f"{v['intro']} solliciter une prolongation du délai concernant {c['sujet']}. "
            + (f"{c['raison'].capitalize()}, " if c['raison'] else "En raison de contraintes imprévues, ")
            + "j'aimerais savoir s'il serait possible de décaler la date de soumission. Je vous remercie par avance pour votre aide."
        ),
        
        "excuse_absence": lambda c, v: (
            (f"Je vous informe que je serai absent " if c['futur'] else "Je vous prie de bien vouloir m'excuser pour mon absence ")
            + (f"le {c['date']} " if c['date'] and c['futur'] else f"du {c['date']} " if c['date'] else "lors de la dernière séance ")
            + (f"en raison d'un {c['raison']}. " if c['raison'] and "problème" in c['raison'] else f"{c['raison']}. " if c['raison'] else "en raison d'un imprévu. ")
            + ("Je m'engage à rattraper les éléments abordés dès mon retour." if c['futur'] else "Je m'engage à rattraper les éléments abordés dans les plus brefs délais.")
        ),
        
        "demande_document": lambda c, v: (
            f"{v['intro']} solliciter, s'il vous plaît, l'obtention d'un document "
            + (f"relatif à {c['sujet']}." if c['sujet'] != "le sujet mentionné" else "administratif.")
        ),
        
        "demande_information": lambda c, v: (
            f"{v['intro']} obtenir des précisions concernant {c['sujet']}. "
            "Pourriez-vous m'apporter des éclaircissements sur ce point ?"
        ),
        
        "relance": lambda c, v: (
            f"Sauf erreur de ma part, je n'ai pas reçu de réponse à mon précédent email concernant {c['sujet']}. "
            "Je me permets de vous relancer afin de m'assurer que ma demande vous est bien parvenue."
        ),
        
        "remerciement": lambda c, v: (
            f"Je tenais à vous remercier sincèrement pour votre aide et pour le temps que vous m'avez accordé "
            f"concernant {c['sujet']}."
        ),
        
        "autre": lambda c, v: (
            f"{v['intro']} vous contacter concernant {c['sujet']}."
        )
    }
    
    template_func = templates_enrichis.get(action, templates_enrichis["autre"])
    return template_func(contexte, variantes)

# =========================
# 6️⃣ Génération MVP améliorée
# =========================
def generate_email_mvp(intention: str, niveau_formalite: str) -> dict:
    # 1. Nettoyage
    intention_propre = nettoyer_intention(intention)
    
    # 2. Validation du ton
    ton_inapproprie, message = detecter_ton_inapproprie(intention_propre)
    if ton_inapproprie:
        # On nettoie automatiquement sans rejeter
        intention_propre = re.sub(r'\b(yo|salut|coucou|wesh|hey)\b', '', intention_propre, flags=re.IGNORECASE)
        intention_propre = re.sub(r'[!]{2,}', '!', intention_propre)
        intention_propre = intention_propre.strip()
    
    # 3. Détection de l'action
    action = detect_action(intention_propre)
    
    # 4. Extraction du contexte
    contexte = extraire_contexte(intention_propre)
    
    # 5. Génération avec variations
    variantes = varier_formulation(action, niveau_formalite)
    
    # 6. Salutations et formules de fin
    salutations = {
        "faible": "Bonjour,",   
        "moyen": "Bonjour Professeur,",
        "élevé": "Monsieur le Professeur / Madame la Professeure,"
    }

    formules_fin = {
        "faible": "Cordialement,",
        "moyen": "Merci pour votre temps et votre compréhension.\n\nCordialement,",
        "élevé": "Je vous prie d'agréer, Monsieur/Madame le Professeur, l'expression de mes salutations distinguées.\n\nCordialement,"
    }
    
    # 7. Construction du corps
    corps_principal = construire_corps_email(action, contexte, niveau_formalite, variantes)
    
    corps = (
        f"{salutations.get(niveau_formalite, salutations['moyen'])}\n\n"
        f"{corps_principal}\n\n"
        f"{formules_fin.get(niveau_formalite, formules_fin['moyen'])}\n\n"
    )
    
    # 8. Objet personnalisé
    objet = generer_objet_personnalise(action, contexte)
    
    return {
        "objet": objet,
        "corps": corps
    }

# =========================
# 7️⃣ Option LLM (Ollama) + fallback
# =========================
def generate_email_with_ollama(intention: str, niveau_formalite: str) -> dict:
    try:
        import requests

        prompt = f"""
Tu es un expert en communication académique.
Transforme une intention brute en un email académique formel.

INTENTION :
"{intention}"

FORMALITÉ :
{niveau_formalite}

CONTRAINTES :
- Reformule l'intention
- Français correct
- Ton académique
- JSON UNIQUEMENT

FORMAT :
{{
  "objet": "...",
  "corps": "..."
}}
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=2
        )

        if response.status_code == 200:
            raw = response.json().get("response", "").strip()
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(raw[start:end])

        return generate_email_mvp(intention, niveau_formalite)

    except Exception:
        return generate_email_mvp(intention, niveau_formalite)

# =========================
# Routes
# =========================
@app.post("/generate-email", response_model=EmailResponse)
async def generate_email(request: EmailRequest):

    if len(request.intention.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="L'intention doit contenir au moins 5 caractères"
        )

    email = generate_email_with_ollama(
        request.intention,
        request.niveau_formalite
    )

    return EmailResponse(**email)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# =========================
# Run
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)