import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
OUTPUT_DIR = DATA_DIR / "output"

# Créer les répertoires s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Email
CANDIDATE_EMAIL = os.getenv("CANDIDATE_EMAIL", "camille.coupet.candidatures@gmail.com")
CANDIDATE_EMAIL_PASSWORD = os.getenv("CANDIDATE_EMAIL_PASSWORD", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "ccoupet02@gmail.com")

# Configuration scraping
SCRAPING_DELAY_MIN = float(os.getenv("SCRAPING_DELAY_MIN", "2"))
SCRAPING_DELAY_MAX = float(os.getenv("SCRAPING_DELAY_MAX", "5"))
MAX_OFFERS_PER_RUN = int(os.getenv("MAX_OFFERS_PER_RUN", "50"))
HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"

# Filtres
LOCATION_KEYWORDS = os.getenv("LOCATION_KEYWORDS", "Lyon,remote,télétravail,distanciel,full remote").split(",")
LOCATION_KEYWORDS = [k.strip().lower() for k in LOCATION_KEYWORDS]

CONTRACT_TYPES = os.getenv("CONTRACT_TYPES", "CDI,CDD").split(",")
CONTRACT_TYPES = [c.strip().upper() for c in CONTRACT_TYPES]

DOMAIN_KEYWORDS = os.getenv(
    "DOMAIN_KEYWORDS",
    "communication,événementiel,event,marketing,chargé de communication,event manager,project manager"
).split(",")
DOMAIN_KEYWORDS = [k.strip().lower() for k in DOMAIN_KEYWORDS]

EXCLUDE_KEYWORDS = os.getenv("EXCLUDE_KEYWORDS", "stage,alternance,apprentissage,intern,internship").split(",")
EXCLUDE_KEYWORDS = [k.strip().lower() for k in EXCLUDE_KEYWORDS]

# Planification
RUN_FREQUENCY = os.getenv("RUN_FREQUENCY", "daily")
RUN_TIME = os.getenv("RUN_TIME", "09:00")

# Chemins de fichiers
CV_BASE_PATH = DATA_DIR / os.getenv("CV_BASE_PATH", "cv_base.json")
COVER_LETTER_TEMPLATE_PATH = DATA_DIR / os.getenv("COVER_LETTER_TEMPLATE_PATH", "cover_letter_template.txt")
DATABASE_PATH = DATA_DIR / os.getenv("DATABASE_PATH", "applications.db")

# LinkedIn (optionnel)
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

# Chrome profile pour persistance des sessions
CHROME_PROFILE_DIR = DATA_DIR / "chrome_profile"
CHROME_PROFILE_DIR.mkdir(exist_ok=True)

# Debug
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Job boards activés
ENABLED_SCRAPERS = [
    "indeed",
    "france_travail",
    "hellowork",
    # "linkedin",  # Nécessite authentification
    # "wttj",
]

# Configuration SMTP Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Informations candidat
CANDIDATE_INFO = {
    "name": "Camille Coupet",
    "email": CANDIDATE_EMAIL,
    "phone": "+33 6 26 72 76 83",
    "location": "Lyon, France"
}
