import requests
import json
from typing import List, Dict
import time

API_URL = "http://localhost:8000"
ENDPOINT = f"{API_URL}/generate-email"

TEST_CASES = [
    {
        "nom": "RDV Soutenance PFE",
        "intention": "je veux un rdv pour ma soutenance pfe lundi prochain",
        "niveau_formalite": "élevé",
        "should_contain": ["rendez-vous", "projet de fin d'études", "lundi prochain"]
    },
    {
        "nom": "Absence TD maladie",
        "intention": "absent au td hier car maladie",
        "niveau_formalite": "moyen",
        "should_contain": ["absence", "raisons médicales", "rattraper"]
    },
    {
        "nom": "Prolongation rapport stage",
        "intention": "besoin de plus de temps pour soumettre mon rapport de stage a cause de problèmes techniques",
        "niveau_formalite": "élevé",
        "should_contain": ["prolongation", "rapport de stage", "difficultés techniques"]
    },
    {
        "nom": "Demande attestation",
        "intention": "svp je veux une attestation de scolarité",
        "niveau_formalite": "moyen",
        "should_contain": ["document", "s'il vous plaît"]
    },
    {
        "nom": "Relance email",
        "intention": "je vous ai envoyé un email la semaine dernière concernant mon pfe mais pas de réponse",
        "niveau_formalite": "moyen",
        "should_contain": ["précédent", "relancer", "projet de fin d'études"]
    },
    {
        "nom": "Langage SMS à nettoyer",
        "intention": "yo prof!! besoin rdv asap pour mon pfa svp mrc",
        "niveau_formalite": "moyen",
        "should_contain": ["rendez-vous", "projet de fin d'année"]
    },
    {
        "nom": "Question note TP",
        "intention": "comprendre pourquoi j'ai eu cette note au tp",
        "niveau_formalite": "faible",
        "should_contain": ["note", "TP"]
    },
    {
        "nom": "Problème de transport",
        "intention": "désolé prof je suis en retard car il y a un problème de transport ce matin",
        "niveau_formalite": "moyen",
        "should_contain": ["absence", "imprévu"]
    },
    {
        "nom": "Fautes de frappe extrêmes",
        "intention": "je vai etre absent le jedi prochain a cause de maladie",
        "niveau_formalite": "moyen",
        "should_contain": ["jeudi prochain", "maladie", "serai absent"]
    }
]

def run_test(tc):
    print(f"\n--- TEST: {tc['nom']} ---")
    try:
        r = requests.post(ENDPOINT, json={"intention": tc["intention"], "niveau_formalite": tc["niveau_formalite"]}, timeout=5)
        if r.status_code != 200:
            print(f"FAILED (HTTP {r.status_code}): {r.text}")
            return False
            
        data = r.json()
        full = (data['objet'] + " " + data['corps']).lower()
        print(f"Objet: {data['objet']}")
        
        success = True
        for word in tc["should_contain"]:
            if word.lower() in full:
                print(f" [V] '{word}' trouvé")
            else:
                print(f" [X] '{word}' MANQUANT")
                success = False
        return success
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    score = 0
    for tc in TEST_CASES:
        if run_test(tc): score += 1
    print(f"\nSCORE FINAL: {score}/{len(TEST_CASES)}")
