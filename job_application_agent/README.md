# 🎯 Agent d'Automatisation de Candidatures - Camille Coupet

Un système automatisé qui recherche les offres d'emploi correspondant à votre profil, génère des CVs et lettres de motivation optimisés, et vous envoie un rapport HTML interactif chaque jour par email.

## 📋 Fonctionnalités

✅ **Recherche automatique** : Scrape les offres depuis Indeed, France Travail, HelloWork, etc.  
✅ **Filtrage intelligent** : Localisation (Lyon/remote), type de contrat (CDI/CDD), domaine (communication/événementiel)  
✅ **CV optimisé** : Génère un CV adapté à chaque offre avec OpenAI  
✅ **Lettre personnalisée** : Crée une lettre de motivation unique pour chaque candidature  
✅ **Rapport HTML** : Document interactif avec toutes les offres, boutons de téléchargement et liens pour postuler  
✅ **Email quotidien** : Reçoit le rapport HTML chaque matin à 9h  
✅ **Suivi centralisé** : Base de données SQLite avec toutes vos candidatures  

## 🚀 Installation Rapide

### Prérequis

- Python 3.11+
- Compte OpenAI (pour génération IA)
- Compte Gmail (pour envoi d'emails)
- Clés API pour les job boards (optionnel)

### Étape 1 : Cloner et configurer

```bash
cd /home/ubuntu/job_application_agent

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 2 : Configurer les variables d'environnement

Ouvrez le fichier `.env` et remplissez les informations :

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-YOUR_KEY_HERE

# Email pour envoyer les candidatures
CANDIDATE_EMAIL=camille.coupet.candidatures@gmail.com
CANDIDATE_EMAIL_PASSWORD=YOUR_APP_PASSWORD

# Email pour recevoir les rapports
NOTIFICATION_EMAIL=ccoupet02@gmail.com
```

#### Comment obtenir les clés ?

**OpenAI API Key** :
1. Allez sur https://platform.openai.com/api-keys
2. Créez une nouvelle clé
3. Copiez-la dans `.env`

**Gmail App Password** :
1. Activez l'authentification 2FA sur votre compte Google
2. Allez sur https://myaccount.google.com/apppasswords
3. Générez un mot de passe pour "Mail"
4. Copiez-le dans `.env`

### Étape 3 : Tester le système

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le script de test
python3 run_daily.py
```

Vous devriez recevoir un email avec le rapport HTML contenant les offres trouvées !

## 📅 Planification Quotidienne

Pour que le système s'exécute automatiquement chaque jour à 9h, utilisez cron :

```bash
# Ouvrir l'éditeur cron
crontab -e

# Ajouter cette ligne (remplacez les chemins)
0 9 * * * /home/ubuntu/job_agent_env/bin/python /home/ubuntu/job_application_agent/run_daily.py >> /home/ubuntu/job_application_agent/data/logs/cron.log 2>&1
```

## 📊 Utilisation

### Recevoir le rapport quotidien

Chaque jour à 9h, vous recevrez un email contenant :

1. **Rapport HTML interactif** avec :
   - Tableau de toutes les offres qualifiées
   - Statistiques (nombre d'offres, taux de succès)
   - Boutons pour télécharger CV et lettre
   - Lien direct pour postuler

2. **Comment utiliser le rapport** :
   - Ouvrez le fichier HTML dans votre navigateur
   - Consultez les offres
   - Téléchargez votre CV et lettre optimisés
   - Cliquez sur "Postuler" pour accéder à l'offre
   - Soumettez votre candidature directement sur le site

### Consulter l'historique

Les candidatures sont enregistrées dans :
- **Base de données** : `data/applications.db`
- **Fichiers générés** : `data/output/`
- **Logs** : `data/logs/`

## ⚙️ Configuration Avancée

### Modifier les critères de filtrage

Éditez le fichier `.env` :

```bash
# Localisation
LOCATION_KEYWORDS=Lyon,remote,télétravail,distanciel

# Types de contrat
CONTRACT_TYPES=CDI,CDD

# Domaines
DOMAIN_KEYWORDS=communication,événementiel,event,marketing

# À exclure
EXCLUDE_KEYWORDS=stage,alternance,apprentissage
```

### Ajouter des job boards

Éditez `config/settings.py` pour activer/désactiver les scrapers :

```python
ENABLED_SCRAPERS = [
    "indeed",
    "france_travail",
    "hellowork",
    # "linkedin",  # Décommenter pour activer
]
```

### Modifier l'heure d'exécution

Changez dans `crontab` :
```bash
# 9h du matin
0 9 * * * ...

# 18h (6 PM)
0 18 * * * ...
```

## 📧 Structure de l'Email Reçu

**Objet** : `📊 Rapport Quotidien - X offres trouvées (Y prêtes)`

**Contenu** :
- Résumé des statistiques
- Fichier HTML en pièce jointe
- Fichier HTML en corps de l'email (pour prévisualisation)

## 🔍 Dépannage

### Je ne reçois pas d'emails

1. **Vérifiez les credentials** :
   - Assurez-vous que `CANDIDATE_EMAIL` et `CANDIDATE_EMAIL_PASSWORD` sont corrects
   - Utilisez un mot de passe d'application Gmail, pas votre mot de passe principal

2. **Vérifiez les logs** :
   ```bash
   tail -f data/logs/app_*.log
   ```

3. **Testez la connexion** :
   ```bash
   python3 -c "
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('votre@email.com', 'votre_mot_de_passe')
   print('Connexion OK')
   server.quit()
   "
   ```

### Les offres ne sont pas trouvées

1. **Vérifiez les critères** : Les offres doivent correspondre à :
   - Localisation : Lyon ou remote
   - Contrat : CDI ou CDD
   - Domaine : communication ou événementiel
   - Pas de stage ni alternance

2. **Vérifiez les logs** :
   ```bash
   grep "Filtering" data/logs/app_*.log
   ```

### Erreur OpenAI

1. **Vérifiez votre clé API** :
   ```bash
   python3 -c "
   import os
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   print('API OK')
   "
   ```

2. **Vérifiez votre crédit** : https://platform.openai.com/account/billing/overview

## 📁 Structure du Projet

```
job_application_agent/
├── config/              # Configuration
├── data/                # Données (CV, lettres, base de données)
├── scrapers/            # Scrapers pour job boards
├── filters/             # Filtrage des offres
├── cv_generator/        # Génération de CV
├── cover_letter/        # Génération de lettres
├── email_manager/       # Gestion des emails
├── tracking/            # Suivi et base de données
├── utils/               # Utilitaires
├── run_daily.py         # Script d'exécution quotidienne
├── main.py              # Script principal
├── html_reporter.py     # Générateur de rapport HTML
├── .env                 # Configuration (À REMPLIR)
└── requirements.txt     # Dépendances Python
```

## 💡 Conseils d'Utilisation

1. **Vérifiez chaque candidature** : Bien que le système soit automatisé, vérifiez toujours que le CV et la lettre sont appropriés avant de postuler.

2. **Personnalisez si nécessaire** : Vous pouvez modifier le CV et la lettre avant de les envoyer.

3. **Suivez vos candidatures** : Notez les offres auxquelles vous avez postulé pour assurer le suivi.

4. **Ajustez les critères** : Si vous recevez trop d'offres non pertinentes, affinez les critères de filtrage.

## 🤝 Support

En cas de problème :
1. Consultez les logs : `data/logs/`
2. Vérifiez la configuration : `.env`
3. Testez chaque composant individuellement

## 📝 Licence

Ce projet est créé pour Camille Coupet par Manus AI.

---

**Bon courage pour vos candidatures ! 🚀**
