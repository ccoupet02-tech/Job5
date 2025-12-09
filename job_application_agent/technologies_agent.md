# Technologies et Outils pour l'Agent d'Automatisation

## Stack Technique Recommandée

### 1. Web Scraping et Automation
- **Selenium**: Automation de navigateur pour interactions complexes (formulaires, Easy Apply)
- **BeautifulSoup4**: Parsing HTML pour extraction de données
- **Requests**: Requêtes HTTP simples
- **Playwright** (alternative): Plus moderne que Selenium, meilleur support JavaScript

### 2. Intelligence Artificielle
- **OpenAI API**: Disponible dans l'environnement (GPT-4.1-mini, GPT-4.1-nano, Gemini-2.5-flash)
- **LangChain**: Framework pour applications AI (agents, RAG)
- **Utilisation**: 
  - Génération de lettres de motivation personnalisées
  - Adaptation du CV selon l'offre
  - Extraction d'informations des offres d'emploi
  - Matching CV/offre

### 3. Génération de Documents
- **python-docx**: Génération de CV au format Word (.docx)
- **ReportLab / FPDF2**: Génération de CV au format PDF
- **Jinja2**: Templates pour génération de contenu
- **WeasyPrint**: Conversion HTML vers PDF (déjà installé)

### 4. Gestion des E-mails
- **smtplib**: Envoi d'emails (bibliothèque standard Python)
- **email**: Construction de messages MIME
- **Gmail API**: Pour utilisation de compte Gmail existant (nécessite OAuth2)
- **Création compte dédié**: Plus simple, utilisation SMTP direct

### 5. Base de Données et Suivi
- **SQLite**: Base de données légère pour tracking des candidatures
- **Pandas + CSV**: Alternative simple pour fichier de suivi Excel/CSV
- **Openpyxl**: Manipulation de fichiers Excel (déjà installé)

### 6. Planification et Scheduling
- **schedule**: Bibliothèque Python pour tâches planifiées
- **APScheduler**: Alternative plus robuste
- **Cron**: Planification système Linux

## Architecture de l'Agent

### Modules Principaux

#### Module 1: Job Scraper
- Scraping des job boards (Indeed, LinkedIn, HelloWork, etc.)
- Scraping des pages carrières d'entreprises
- Extraction des informations: titre, description, entreprise, lieu, type de contrat, langue

#### Module 2: Job Filter
- Filtrage par localisation (Lyon, remote)
- Filtrage par type de contrat (CDI, CDD)
- Filtrage par domaine (communication, événementiel)
- Exclusion (stages, alternances)
- Détection de langue (français, anglais)
- Vérification des doublons

#### Module 3: CV Optimizer
- Analyse de l'offre d'emploi avec AI
- Extraction des compétences requises
- Adaptation du CV selon l'offre
- Optimisation ATS (mots-clés, format)
- Génération en français ou anglais selon la langue de l'offre
- Export en PDF et/ou Word

#### Module 4: Cover Letter Generator
- Génération de lettre de motivation personnalisée avec AI
- Utilisation de la lettre de référence comme base
- Adaptation au poste et à l'entreprise
- Génération en français ou anglais
- Maintien de l'alignement avec le CV

#### Module 5: Application Submitter
- Détection du type de candidature (Easy Apply, email, formulaire)
- Automation LinkedIn Easy Apply avec Selenium
- Envoi d'emails avec CV + lettre
- Remplissage de formulaires web
- Gestion des erreurs et retry

#### Module 6: Email Manager
- Création/utilisation d'adresse email dédiée
- Envoi des candidatures par email
- Envoi de notifications à l'utilisateur
- Gestion des templates d'email

#### Module 7: Tracking & Notification
- Enregistrement de chaque candidature dans base de données
- Export CSV/Excel pour suivi
- Envoi de notification par email après chaque candidature
- Statistiques et rapports

## Défis Techniques Identifiés

### 1. Protection Anti-Bot
- **Problème**: CAPTCHAs, détection de bot, rate limiting
- **Solutions**: 
  - Utilisation de delays aléatoires
  - User-Agent rotation
  - Utilisation de proxies si nécessaire
  - Selenium avec profil Chrome réaliste
  - Services de résolution CAPTCHA (2Captcha, Anti-Captcha)

### 2. Absence d'APIs Publiques
- **Problème**: La plupart des job boards n'ont pas d'API gratuite
- **Solutions**:
  - Web scraping avec respect des robots.txt
  - Rate limiting pour éviter le blocage
  - Caching des résultats

### 3. Variabilité des Formats
- **Problème**: Chaque site a sa propre structure
- **Solutions**:
  - Scrapers spécifiques par site
  - Patterns génériques pour sites carrières entreprises
  - Maintenance régulière des scrapers

### 4. Authentification LinkedIn
- **Problème**: LinkedIn nécessite une connexion
- **Solutions**:
  - Utilisation de cookies de session persistants
  - Selenium avec profil Chrome sauvegardé
  - Éviter l'approche avec identifiants en dur (préférence utilisateur)

### 5. Détection de Doublons
- **Problème**: Même offre sur plusieurs sites
- **Solutions**:
  - Hashing du titre + entreprise + lieu
  - Comparaison de similarité avec AI
  - Base de données des offres déjà traitées

## Packages Python Nécessaires

```bash
# Web scraping et automation
pip install selenium webdriver-manager playwright
pip install beautifulsoup4 requests lxml

# AI et NLP
pip install openai langchain langchain-openai
pip install tiktoken  # Pour compter tokens OpenAI

# Génération de documents
pip install python-docx reportlab jinja2
pip install markdown2  # Conversion markdown vers HTML

# Email
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
# (si utilisation Gmail API)

# Base de données et suivi
pip install sqlalchemy
# pandas et openpyxl déjà installés

# Planification
pip install schedule apscheduler

# Utilitaires
pip install python-dotenv  # Gestion variables d'environnement
pip install tqdm  # Barres de progression
pip install loguru  # Logging avancé
```

## Considérations Éthiques et Légales

### Respect des Terms of Service
- Vérifier les ToS de chaque plateforme
- Respecter les robots.txt
- Implémenter rate limiting
- Ne pas surcharger les serveurs

### Protection des Données
- Stockage sécurisé des credentials
- Chiffrement des données sensibles
- Respect RGPD

### Qualité des Candidatures
- S'assurer que les candidatures sont pertinentes
- Éviter le spam
- Personnalisation réelle des lettres de motivation
- Vérification humaine recommandée avant envoi massif

## Recommandations d'Implémentation

### Phase 1: MVP (Minimum Viable Product)
1. Scraper pour 2-3 job boards principaux (Indeed, LinkedIn, France Travail)
2. Filtrage basique
3. Génération CV/lettre avec OpenAI
4. Envoi par email uniquement
5. Tracking CSV simple

### Phase 2: Extension
1. Ajout de plus de job boards
2. Scraping des sites carrières entreprises
3. Support Easy Apply LinkedIn
4. Remplissage de formulaires web
5. Base de données SQLite
6. Interface de configuration

### Phase 3: Optimisation
1. Amélioration anti-détection
2. Gestion avancée des erreurs
3. Retry automatique
4. Dashboard de suivi
5. Statistiques et analytics
6. Tests A/B sur les lettres de motivation
