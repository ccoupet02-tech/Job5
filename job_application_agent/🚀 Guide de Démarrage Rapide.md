# 🚀 Guide de Démarrage Rapide

## Pour les Utilisateurs Sans Expérience en Code

Ce guide vous explique comment utiliser le système d'automatisation de candidatures **sans toucher au code**.

---

## 📋 Étape 1 : Préparation (5 minutes)

### Créer une adresse email dédiée (optionnel mais recommandé)

1. Allez sur https://mail.google.com
2. Cliquez sur "Créer un compte"
3. Remplissez le formulaire avec :
   - Prénom : Camille
   - Nom : Coupet
   - Email : `camille.coupet.candidatures@gmail.com`
   - Mot de passe : Créez un mot de passe fort

**Pourquoi ?** Cela sépare vos candidatures de votre email personnel.

### Activer l'authentification 2FA (sécurité)

1. Allez sur https://myaccount.google.com
2. Cliquez sur "Sécurité"
3. Activez "Authentification à 2 facteurs"

### Générer un mot de passe d'application

1. Allez sur https://myaccount.google.com/apppasswords
2. Sélectionnez "Mail" et "Windows"
3. Google génère un mot de passe (16 caractères)
4. **Copiez ce mot de passe quelque part de sûr**

---

## 🔑 Étape 2 : Obtenir les Clés API (10 minutes)

### Clé OpenAI (pour la génération IA)

1. Allez sur https://platform.openai.com/signup
2. Créez un compte ou connectez-vous
3. Allez sur https://platform.openai.com/api-keys
4. Cliquez sur "+ Create new secret key"
5. Copiez la clé (elle commence par `sk-`)

**Coût** : Environ 0,01€ par jour (très peu coûteux)

---

## ⚙️ Étape 3 : Configuration (5 minutes)

### Ouvrir le fichier de configuration

1. Ouvrez le dossier : `/home/ubuntu/job_application_agent`
2. Trouvez le fichier `.env` (fichier texte)
3. Ouvrez-le avec un éditeur de texte

### Remplir les informations

Remplacez les valeurs suivantes :

```
# Votre clé OpenAI (obtenue à l'étape 2)
OPENAI_API_KEY=sk-VOTRE_CLE_ICI

# Email dédié pour les candidatures
CANDIDATE_EMAIL=camille.coupet.candidatures@gmail.com

# Mot de passe d'application (obtenu à l'étape 1)
CANDIDATE_EMAIL_PASSWORD=VOTRE_MOT_DE_PASSE_ICI

# Email où vous recevrez les rapports
NOTIFICATION_EMAIL=ccoupet02@gmail.com
```

**Sauvegardez le fichier** (Ctrl+S)

---

## ✅ Étape 4 : Test (2 minutes)

### Lancer le système une première fois

1. Ouvrez un terminal
2. Tapez les commandes suivantes :

```bash
cd /home/ubuntu/job_application_agent
source ../job_agent_env/bin/activate
python3 run_daily.py
```

3. Attendez 2-3 minutes
4. Vérifiez votre email (dossier Inbox ou Spam)

**Vous devriez recevoir un email avec le rapport HTML !**

---

## 📅 Étape 5 : Planification Automatique (5 minutes)

Pour que le système s'exécute **automatiquement chaque jour à 9h** :

### Sur Linux/Mac

1. Ouvrez un terminal
2. Tapez : `crontab -e`
3. Ajoutez cette ligne à la fin du fichier :

```
0 9 * * * /home/ubuntu/job_agent_env/bin/python /home/ubuntu/job_application_agent/run_daily.py >> /home/ubuntu/job_application_agent/data/logs/cron.log 2>&1
```

4. Sauvegardez (Ctrl+X, puis Y, puis Entrée)

### Sur Windows

1. Ouvrez "Planificateur de tâches"
2. Cliquez sur "Créer une tâche basique"
3. Nom : "Job Application Agent"
4. Déclencheur : "Quotidien" à 9h00
5. Action : Lancer le programme
   - Programme : `C:\Python311\python.exe`
   - Arguments : `C:\chemin\vers\run_daily.py`

---

## 📧 Étape 6 : Utiliser le Rapport Quotidien

Chaque jour à 9h, vous recevrez un email avec :

### 1. Rapport HTML (pièce jointe)

- Téléchargez le fichier `.html`
- Ouvrez-le dans votre navigateur
- Vous verrez un tableau avec toutes les offres

### 2. Pour chaque offre :

**Bouton "📄 CV"** : Télécharge votre CV optimisé pour cette offre
**Bouton "📝 Lettre"** : Télécharge votre lettre de motivation personnalisée
**Bouton "🔗 Postuler"** : Ouvre l'offre sur le site

### 3. Processus de candidature :

1. Téléchargez le CV et la lettre
2. Cliquez sur "Postuler"
3. Allez sur le site de l'offre
4. Collez le contenu de la lettre dans le formulaire
5. Attachez le CV
6. Cliquez sur "Envoyer"

---

## 🎯 Résumé du Flux

```
Chaque jour à 9h :
    ↓
Le système recherche les offres
    ↓
Filtre selon vos critères
    ↓
Génère un CV optimisé pour chaque offre
    ↓
Génère une lettre de motivation personnalisée
    ↓
Crée un rapport HTML
    ↓
Vous envoie le rapport par email
    ↓
Vous consultez le rapport
    ↓
Vous téléchargez CV et lettre
    ↓
Vous postulez directement sur les sites
```

---

## ❓ Questions Fréquentes

### Q: Je ne reçois pas d'email

**R:** 
1. Vérifiez que votre mot de passe d'application est correct dans `.env`
2. Vérifiez le dossier Spam
3. Assurez-vous d'avoir activé l'authentification 2FA

### Q: Combien ça coûte ?

**R:** 
- OpenAI : ~0,01€ par jour (très peu)
- Gmail : Gratuit
- Total : Moins de 1€ par mois

### Q: Puis-je modifier les critères de recherche ?

**R:** Oui ! Éditez le fichier `.env` :
- `LOCATION_KEYWORDS` : Villes
- `CONTRACT_TYPES` : CDI, CDD
- `DOMAIN_KEYWORDS` : Domaines d'activité

### Q: Que faire si une offre n'est pas pertinente ?

**R:** Vous pouvez l'ignorer. Le rapport est juste pour vous informer. Vous décidez de postuler ou non.

### Q: Comment arrêter le système ?

**R:** Supprimez la ligne du crontab :
```bash
crontab -e
# Supprimez la ligne contenant "run_daily.py"
```

---

## 📞 Support

Si vous avez des problèmes :

1. Consultez le fichier de log : `data/logs/app_*.log`
2. Vérifiez votre configuration `.env`
3. Relancez le test (étape 4)

---

## ✨ Prochaines Étapes

Une fois que le système fonctionne :

1. **Consultez vos rapports quotidiens** chaque matin
2. **Téléchargez vos documents** optimisés
3. **Postulez directement** sur les sites
4. **Suivez vos candidatures** dans la base de données

**Bonne chance pour vos candidatures ! 🚀**

---

*Créé par Manus AI pour Camille Coupet*
