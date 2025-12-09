# 📦 LIVRAISON - Agent d'Automatisation de Candidatures

**Pour :** Camille Coupet  
**Date :** 03 Décembre 2025  
**Créé par :** Manus AI

---

## 🎯 Qu'avez-vous reçu ?

Un **système complet et automatisé** qui :

✅ Recherche les offres d'emploi chaque jour  
✅ Filtre selon vos critères (Lyon/remote, CDI/CDD, communication/événementiel)  
✅ Génère un CV optimisé pour CHAQUE offre  
✅ Génère une lettre de motivation personnalisée  
✅ Crée un rapport HTML interactif  
✅ Vous envoie le rapport par email chaque matin à 9h  
✅ Centralise tout dans une base de données  

---

## 📂 Fichiers Livrés

### 📍 Localisation
```
/home/ubuntu/job_application_agent/
```

### 📋 Documentation (À LIRE EN PREMIER)

| Fichier | Contenu |
|---------|---------|
| **GUIDE_DEMARRAGE.md** | 👈 **COMMENCEZ ICI** - Guide pas-à-pas pour non-codeurs |
| **README.md** | Documentation complète du système |
| **.env.example** | Exemple de configuration |

### ⚙️ Configuration

| Fichier | À Faire |
|---------|---------|
| **.env** | ✏️ **À REMPLIR** avec vos clés API et emails |
| **config/settings.py** | Configuration générale (optionnel) |

### 📊 Données

| Dossier | Contenu |
|---------|---------|
| **data/cv_base.json** | Votre CV structuré |
| **data/cover_letter_template.txt** | Votre lettre de motivation template |
| **data/output/** | CVs et lettres générés |
| **data/logs/** | Fichiers de log |
| **data/applications.db** | Base de données SQLite |

### 🔧 Modules Python

| Module | Fonction |
|--------|----------|
| **scrapers/** | Recherche les offres sur Indeed, France Travail, etc. |
| **filters/** | Filtre selon vos critères |
| **cv_generator/** | Génère CVs optimisés avec OpenAI |
| **cover_letter/** | Génère lettres de motivation |
| **email_manager/** | Envoie les emails |
| **tracking/** | Suivi et base de données |
| **utils/** | Utilitaires (IA, web, logging) |
| **html_reporter.py** | Crée le rapport HTML interactif |

### 🚀 Scripts Exécutables

| Script | Utilisation |
|--------|------------|
| **run_daily.py** | Lance le processus quotidien (utilisé par cron) |
| **main.py** | Script principal (pour tests) |

---

## 🎬 Démarrage en 3 Étapes

### Étape 1 : Lire le guide (5 min)
```bash
cat /home/ubuntu/job_application_agent/GUIDE_DEMARRAGE.md
```

### Étape 2 : Configurer (.env) (5 min)
```bash
# Ouvrir le fichier .env
nano /home/ubuntu/job_application_agent/.env

# Remplir :
# - OPENAI_API_KEY
# - CANDIDATE_EMAIL
# - CANDIDATE_EMAIL_PASSWORD
# - NOTIFICATION_EMAIL
```

### Étape 3 : Tester (2 min)
```bash
cd /home/ubuntu/job_application_agent
source ../job_agent_env/bin/activate
python3 run_daily.py
```

**Vous recevrez un email avec le rapport HTML !**

---

## 📧 Ce que Vous Recevrez Chaque Jour

### Email à 9h du matin

**Objet :** `📊 Rapport Quotidien - X offres trouvées (Y prêtes)`

**Contenu :**
1. Résumé des statistiques
2. Fichier HTML en pièce jointe
3. Fichier HTML en aperçu dans l'email

### Rapport HTML (à ouvrir dans le navigateur)

```
┌─────────────────────────────────────────┐
│  🎯 Offres d'Emploi Qualifiées          │
│  Candidatures automatisées et           │
│  personnalisées pour Camille Coupet     │
├─────────────────────────────────────────┤
│  📊 Statistiques                        │
│  • 15 offres trouvées                   │
│  • 12 candidatures prêtes               │
│  • 3 erreurs                            │
├─────────────────────────────────────────┤
│  📋 Tableau des Offres                  │
│  ┌─────────────────────────────────────┐│
│  │ N° │ Poste │ Entreprise │ Actions  ││
│  ├─────────────────────────────────────┤│
│  │ 1  │ Chargée de communication │     ││
│  │    │ Entreprise XYZ          │ 📄📝🔗││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

**Pour chaque offre :**
- 📄 **CV** : Télécharger le CV optimisé
- 📝 **Lettre** : Télécharger la lettre de motivation
- 🔗 **Postuler** : Lien direct vers l'offre

---

## 🔑 Clés API Nécessaires

### 1. OpenAI API Key (OBLIGATOIRE)

**Où l'obtenir :**
1. https://platform.openai.com/signup
2. https://platform.openai.com/api-keys
3. Cliquez "+ Create new secret key"

**Coût :** ~0,01€ par jour (très peu)

**Format :** `sk-...`

### 2. Gmail App Password (OBLIGATOIRE)

**Où l'obtenir :**
1. https://myaccount.google.com
2. Sécurité → Authentification 2FA (activer)
3. https://myaccount.google.com/apppasswords
4. Sélectionnez "Mail" et "Windows"
5. Copiez le mot de passe (16 caractères)

---

## 📅 Planification Automatique

### Linux/Mac (cron)

```bash
crontab -e

# Ajouter cette ligne :
0 9 * * * /home/ubuntu/job_agent_env/bin/python /home/ubuntu/job_application_agent/run_daily.py >> /home/ubuntu/job_application_agent/data/logs/cron.log 2>&1
```

### Windows (Planificateur de tâches)

1. Ouvrez "Planificateur de tâches"
2. "Créer une tâche basique"
3. Nom : "Job Application Agent"
4. Déclencheur : Quotidien à 9h00
5. Action : Lancer le programme
   - Programme : `C:\Python311\python.exe`
   - Arguments : `C:\chemin\vers\run_daily.py`

---

## 🎯 Flux de Travail Quotidien

```
9h00 du matin
    ↓
[Système] Recherche les offres
    ↓
[Système] Filtre selon vos critères
    ↓
[Système] Génère CV optimisés
    ↓
[Système] Génère lettres personnalisées
    ↓
[Système] Crée rapport HTML
    ↓
[Système] Envoie email
    ↓
[Vous] Recevez l'email
    ↓
[Vous] Ouvrez le rapport HTML
    ↓
[Vous] Téléchargez CV et lettre
    ↓
[Vous] Postulez sur les sites
```

---

## ✨ Fonctionnalités Avancées

### Modifier les critères de recherche

Éditez `.env` :
```bash
# Localisation
LOCATION_KEYWORDS=Lyon,remote,télétravail

# Types de contrat
CONTRACT_TYPES=CDI,CDD

# Domaines
DOMAIN_KEYWORDS=communication,événementiel,event,marketing

# À exclure
EXCLUDE_KEYWORDS=stage,alternance
```

### Activer/désactiver les job boards

Éditez `config/settings.py` :
```python
ENABLED_SCRAPERS = [
    "indeed",
    "france_travail",
    "hellowork",
    # "linkedin",  # Décommenter pour activer
]
```

### Consulter l'historique

```bash
# Voir les logs
tail -f data/logs/app_*.log

# Voir les candidatures
sqlite3 data/applications.db "SELECT * FROM applications;"
```

---

## 🆘 Dépannage Rapide

| Problème | Solution |
|----------|----------|
| Pas d'emails reçus | Vérifiez `.env` et le dossier Spam |
| Erreur OpenAI | Vérifiez votre clé API et votre crédit |
| Pas d'offres trouvées | Vérifiez les critères de filtrage |
| Cron ne s'exécute pas | Vérifiez les chemins dans la commande cron |

---

## 📞 Support & Questions

### Fichiers de log
```bash
# Voir les erreurs
tail -50 /home/ubuntu/job_application_agent/data/logs/app_*.log

# Voir les logs de cron
tail -50 /home/ubuntu/job_application_agent/data/logs/cron.log
```

### Tester chaque composant

```bash
# Tester OpenAI
python3 -c "from openai import OpenAI; print('OK')"

# Tester Gmail
python3 -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587); print('OK')"

# Tester la base de données
python3 -c "import sqlite3; sqlite3.connect('data/applications.db'); print('OK')"
```

---

## 📊 Statistiques & Suivi

### Voir vos candidatures

```bash
# Ouvrir la base de données
sqlite3 /home/ubuntu/job_application_agent/data/applications.db

# Voir toutes les candidatures
SELECT job_title, company, applied_at, success FROM applications;

# Voir les statistiques
SELECT COUNT(*) as total, SUM(success) as successful FROM applications;
```

### Exporter en Excel

Les rapports HTML incluent les données que vous pouvez copier/coller dans Excel.

---

## 🎓 Prochaines Étapes

1. **Lisez le GUIDE_DEMARRAGE.md** (5 min)
2. **Remplissez le fichier .env** (5 min)
3. **Lancez le test** (2 min)
4. **Configurez cron** (5 min)
5. **Recevez votre premier rapport** (demain à 9h)

---

## ✅ Checklist de Configuration

- [ ] J'ai créé une adresse email dédiée (optionnel)
- [ ] J'ai obtenu une clé OpenAI
- [ ] J'ai généré un mot de passe d'application Gmail
- [ ] J'ai rempli le fichier `.env`
- [ ] J'ai testé le système avec `python3 run_daily.py`
- [ ] J'ai configuré cron pour l'exécution quotidienne
- [ ] J'ai reçu mon premier rapport HTML par email

---

## 🎉 Résumé

Vous avez maintenant un **système complet et automatisé** qui :

- ✅ Recherche les offres chaque jour
- ✅ Génère des CVs et lettres optimisés
- ✅ Vous envoie un rapport HTML interactif
- ✅ Centralise tout dans une base de données
- ✅ Ne nécessite aucune connaissance en code

**Il vous suffit de :**
1. Remplir le fichier `.env`
2. Lancer le test
3. Configurer cron
4. Consulter vos rapports quotidiens

---

## 📝 Notes Importantes

- **Coût :** Moins de 1€ par mois (OpenAI + Gmail gratuit)
- **Sécurité :** Vos données restent locales, pas de cloud
- **Confidentialité :** Aucune donnée personnelle n'est partagée
- **Contrôle :** Vous décidez de chaque candidature

---

**Créé avec ❤️ par Manus AI pour Camille Coupet**

*Bonne chance pour vos candidatures ! 🚀*
