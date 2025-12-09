# Architecture de l'Agent d'Automatisation de Candidatures

## Vue d'Ensemble

L'agent d'automatisation est conçu comme un système modulaire et extensible composé de 7 modules principaux qui travaillent ensemble pour automatiser le processus complet de candidature.

## Structure du Projet

```
job_application_agent/
├── config/
│   ├── __init__.py
│   ├── settings.py              # Configuration générale
│   └── credentials.py           # Gestion des credentials (gitignored)
├── data/
│   ├── cv_base.json             # CV structuré de Camille
│   ├── cover_letter_template.txt # Template lettre de motivation
│   ├── applications.db          # Base de données SQLite
│   └── logs/                    # Fichiers de logs
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py          # Classe abstraite de base
│   ├── indeed_scraper.py        # Scraper Indeed
│   ├── linkedin_scraper.py      # Scraper LinkedIn
│   ├── france_travail_scraper.py # Scraper France Travail
│   ├── hellowork_scraper.py     # Scraper HelloWork
│   ├── wttj_scraper.py          # Scraper Welcome to the Jungle
│   └── company_careers_scraper.py # Scraper générique sites entreprises
├── filters/
│   ├── __init__.py
│   ├── location_filter.py       # Filtrage par localisation
│   ├── contract_filter.py       # Filtrage par type de contrat
│   ├── domain_filter.py         # Filtrage par domaine
│   ├── language_detector.py     # Détection de langue
│   └── duplicate_detector.py    # Détection de doublons
├── cv_generator/
│   ├── __init__.py
│   ├── cv_optimizer.py          # Optimisation CV avec AI
│   ├── cv_templates.py          # Templates de CV
│   ├── docx_generator.py        # Génération Word
│   └── pdf_generator.py         # Génération PDF
├── cover_letter/
│   ├── __init__.py
│   └── generator.py             # Génération lettre de motivation avec AI
├── applicators/
│   ├── __init__.py
│   ├── base_applicator.py       # Classe abstraite de base
│   ├── email_applicator.py      # Candidature par email
│   ├── linkedin_easy_apply.py   # LinkedIn Easy Apply
│   └── form_applicator.py       # Formulaires web génériques
├── email_manager/
│   ├── __init__.py
│   ├── sender.py                # Envoi d'emails
│   └── notifier.py              # Notifications utilisateur
├── tracking/
│   ├── __init__.py
│   ├── database.py              # Gestion base de données
│   ├── exporter.py              # Export CSV/Excel
│   └── statistics.py            # Statistiques
├── utils/
│   ├── __init__.py
│   ├── logger.py                # Configuration logging
│   ├── ai_helper.py             # Helpers OpenAI
│   └── web_utils.py             # Utilitaires web (delays, user-agents)
├── main.py                      # Point d'entrée principal
├── scheduler.py                 # Planification des tâches
├── requirements.txt             # Dépendances Python
├── .env.example                 # Exemple de fichier d'environnement
└── README.md                    # Documentation
```

## Flux de Travail Principal

### 1. Initialisation
```
main.py démarre
  ↓
Chargement de la configuration
  ↓
Initialisation de la base de données
  ↓
Vérification des credentials
```

### 2. Recherche d'Offres
```
Pour chaque scraper activé:
  ↓
Scraping des offres
  ↓
Extraction des données (titre, description, entreprise, lieu, URL, etc.)
  ↓
Stockage temporaire en mémoire
```

### 3. Filtrage
```
Pour chaque offre scrapée:
  ↓
Vérification doublon (base de données)
  ↓
Filtrage localisation (Lyon ou remote)
  ↓
Filtrage type de contrat (CDI/CDD)
  ↓
Filtrage domaine (communication/événementiel)
  ↓
Exclusion (stages/alternances)
  ↓
Détection de langue (français/anglais)
  ↓
Si tous les critères sont OK → Offre qualifiée
```

### 4. Génération de Documents
```
Pour chaque offre qualifiée:
  ↓
Analyse de l'offre avec OpenAI
  ↓
Extraction des compétences clés
  ↓
Adaptation du CV (ajout/modification/suppression d'éléments)
  ↓
Optimisation ATS (mots-clés)
  ↓
Génération CV en français ou anglais selon langue de l'offre
  ↓
Export en PDF
  ↓
Génération lettre de motivation personnalisée
  ↓
Export en PDF ou texte selon besoin
```

### 5. Candidature
```
Détection du type de candidature:
  ↓
Si Easy Apply (LinkedIn):
  → Automation Selenium
  → Remplissage formulaire
  → Upload CV
  → Soumission
  ↓
Si Email:
  → Construction email avec corps personnalisé
  → Attachement CV + lettre
  → Envoi via SMTP
  ↓
Si Formulaire Web:
  → Automation Selenium
  → Remplissage champs
  → Upload documents
  → Soumission
```

### 6. Tracking et Notification
```
Après chaque candidature:
  ↓
Enregistrement dans base de données:
  - Date et heure
  - Offre (titre, entreprise, URL)
  - Type de candidature
  - Documents envoyés (chemins)
  - Statut (succès/échec)
  ↓
Envoi notification email à ccoupet02@gmail.com:
  - Lien de l'offre
  - Fichiers envoyés en attachement
  - Date
  ↓
Mise à jour du fichier CSV de suivi
```

## Modules Détaillés

### Module 1: Scrapers

**Responsabilités:**
- Récupération des offres d'emploi depuis diverses sources
- Normalisation des données extraites
- Gestion des erreurs et retry

**Classe de Base (base_scraper.py):**
```python
class BaseScraper:
    def __init__(self, config):
        self.config = config
        self.driver = None  # Selenium WebDriver si nécessaire
        
    def scrape(self) -> List[JobOffer]:
        """Méthode abstraite à implémenter par chaque scraper"""
        raise NotImplementedError
        
    def parse_job_offer(self, element) -> JobOffer:
        """Parse un élément HTML en objet JobOffer"""
        raise NotImplementedError
        
    def setup_driver(self):
        """Configure Selenium WebDriver avec options anti-détection"""
        pass
        
    def close_driver(self):
        """Ferme le driver proprement"""
        pass
```

**Données Extraites (JobOffer):**
```python
@dataclass
class JobOffer:
    id: str  # Hash unique
    title: str
    company: str
    location: str
    contract_type: str  # CDI, CDD, etc.
    description: str
    requirements: str
    url: str
    source: str  # indeed, linkedin, etc.
    language: str  # fr, en
    posted_date: datetime
    application_type: str  # email, easy_apply, form
    application_url: str  # URL ou email
    scraped_at: datetime
```

### Module 2: Filters

**Responsabilités:**
- Application des critères de filtrage
- Détection de doublons
- Détection de langue

**Filtres Implémentés:**

1. **LocationFilter**: Vérifie si le lieu contient "Lyon" ou "remote"/"télétravail"
2. **ContractFilter**: Vérifie si le type de contrat est CDI ou CDD
3. **DomainFilter**: Utilise AI pour vérifier si le poste est lié à communication/événementiel
4. **LanguageDetector**: Détecte la langue (français/anglais) via analyse du texte
5. **DuplicateDetector**: Compare avec les offres déjà traitées (hash ou similarité)

### Module 3: CV Generator

**Responsabilités:**
- Analyse de l'offre d'emploi
- Adaptation du CV selon les exigences
- Génération de documents optimisés ATS

**Processus d'Optimisation:**

1. **Analyse de l'offre avec OpenAI:**
   - Extraction des compétences requises
   - Identification des mots-clés importants
   - Détermination du niveau d'expérience attendu

2. **Adaptation du CV:**
   - Réorganisation des expériences (mettre en avant les plus pertinentes)
   - Ajout de mots-clés pertinents
   - Modification des descriptions pour matcher l'offre
   - Ajustement du profil/résumé

3. **Optimisation ATS:**
   - Format simple et lisible
   - Utilisation de sections standard
   - Inclusion des mots-clés exacts de l'offre
   - Éviter les tableaux, images, en-têtes/pieds de page complexes

4. **Génération:**
   - Si offre en français → CV en français
   - Si offre en anglais → CV en anglais (traduction + adaptation)
   - Export en PDF (format universel)

### Module 4: Cover Letter Generator

**Responsabilités:**
- Génération de lettres de motivation personnalisées
- Maintien de la cohérence avec le CV
- Adaptation à la langue de l'offre

**Processus de Génération:**

1. **Analyse du contexte:**
   - Offre d'emploi (titre, entreprise, description)
   - CV adapté
   - Lettre de motivation de référence

2. **Génération avec OpenAI:**
   - Prompt incluant la lettre de référence comme exemple de style
   - Instructions pour personnaliser selon l'offre
   - Maintien du ton professionnel et motivé
   - Mise en avant des expériences pertinentes

3. **Validation:**
   - Vérification de la longueur (max 1 page)
   - Vérification de la langue
   - Vérification de la cohérence avec le CV

### Module 5: Applicators

**Responsabilités:**
- Soumission des candidatures selon le type
- Gestion des erreurs et retry
- Capture des confirmations

**Types d'Application:**

1. **EmailApplicator:**
   - Construction du corps d'email
   - Attachement des documents
   - Envoi via SMTP
   - Gestion des erreurs d'envoi

2. **LinkedInEasyApply:**
   - Automation Selenium
   - Navigation vers l'offre
   - Clic sur "Easy Apply"
   - Remplissage du formulaire
   - Upload du CV
   - Réponse aux questions additionnelles (si possible)
   - Soumission

3. **FormApplicator:**
   - Automation Selenium
   - Détection des champs du formulaire
   - Remplissage automatique
   - Upload des documents
   - Soumission

### Module 6: Email Manager

**Responsabilités:**
- Envoi des candidatures par email
- Envoi des notifications à l'utilisateur
- Gestion de l'adresse email dédiée

**Configuration Email:**

Option choisie: **Création d'une adresse email dédiée**

- Format: camille.coupet.candidatures@gmail.com (ou similaire)
- Configuration SMTP Gmail
- Utilisation pour toutes les candidatures
- Notifications envoyées à ccoupet02@gmail.com

**Templates d'Email:**

1. **Email de candidature:**
```
Objet: Candidature [Titre du poste] - Camille Coupet

Madame, Monsieur,

[Corps personnalisé généré par AI]

Cordialement,
Camille Coupet
+33 6 26 72 76 83
```

2. **Email de notification:**
```
Objet: ✅ Candidature envoyée - [Titre du poste] chez [Entreprise]

Bonjour Camille,

Une candidature a été envoyée avec succès :

📋 Poste: [Titre]
🏢 Entreprise: [Nom]
📍 Lieu: [Localisation]
🔗 Lien: [URL]
📅 Date: [Date et heure]
📎 Documents envoyés:
   - CV_[nom].pdf
   - Lettre_motivation_[nom].pdf

Type de candidature: [Email/Easy Apply/Formulaire]

Bonne chance !
```

### Module 7: Tracking

**Responsabilités:**
- Enregistrement de toutes les candidatures
- Export des données
- Génération de statistiques

**Base de Données SQLite:**

Tables:
1. **applications**: Toutes les candidatures envoyées
2. **job_offers**: Toutes les offres scrapées
3. **errors**: Logs des erreurs rencontrées

**Export CSV:**

Colonnes:
- Date
- Heure
- Titre du poste
- Entreprise
- Lieu
- Type de contrat
- URL de l'offre
- Type de candidature
- Statut
- Chemin CV
- Chemin lettre de motivation

## Configuration

**Fichier .env:**
```
# OpenAI
OPENAI_API_KEY=sk-...

# Email dédié pour candidatures
CANDIDATE_EMAIL=camille.coupet.candidatures@gmail.com
CANDIDATE_EMAIL_PASSWORD=...

# Email pour notifications
NOTIFICATION_EMAIL=ccoupet02@gmail.com

# Configuration scraping
SCRAPING_DELAY_MIN=2
SCRAPING_DELAY_MAX=5
MAX_OFFERS_PER_RUN=50

# Filtres
LOCATION_KEYWORDS=Lyon,remote,télétravail,distanciel
CONTRACT_TYPES=CDI,CDD
DOMAIN_KEYWORDS=communication,événementiel,event,marketing

# Planification
RUN_FREQUENCY=daily
RUN_TIME=09:00
```

## Planification et Exécution

**Exécution Quotidienne:**

L'agent s'exécute automatiquement chaque jour à 9h00 via un scheduler Python ou un cron job.

**Processus d'exécution:**
1. Lancement du script
2. Scraping de toutes les sources
3. Filtrage des offres
4. Pour chaque offre qualifiée:
   - Génération des documents
   - Soumission de la candidature
   - Notification
5. Génération du rapport quotidien
6. Arrêt propre

**Gestion des Erreurs:**
- Logging de toutes les erreurs
- Retry automatique (max 3 tentatives)
- Notification en cas d'échec critique
- Continuation avec les autres offres en cas d'erreur sur une offre

## Sécurité et Bonnes Pratiques

1. **Credentials:**
   - Stockage dans .env (gitignored)
   - Chiffrement des mots de passe sensibles
   - Pas de credentials en dur dans le code

2. **Rate Limiting:**
   - Délais aléatoires entre requêtes (2-5 secondes)
   - Limitation du nombre d'offres par run (50 max)
   - Respect des robots.txt

3. **Anti-Détection:**
   - User-Agent réaliste
   - Selenium avec profil Chrome
   - Cookies persistants
   - Comportement humain simulé (scrolling, mouvements de souris)

4. **Logging:**
   - Logs détaillés de toutes les opérations
   - Rotation des logs
   - Niveaux: DEBUG, INFO, WARNING, ERROR, CRITICAL

5. **Backup:**
   - Sauvegarde quotidienne de la base de données
   - Archivage des CVs et lettres générés
   - Export CSV régulier
