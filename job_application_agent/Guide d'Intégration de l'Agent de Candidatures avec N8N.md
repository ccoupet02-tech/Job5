# Guide d'Intégration de l'Agent de Candidatures avec N8N

Ce guide explique comment intégrer le cœur de l'agent d'automatisation (l'optimisation IA du CV/Lettre et la génération de PDF) dans un workflow N8N pour garantir une exécution quotidienne fiable.

---

## 1. Pourquoi N8N ?

L'agent Python que j'ai développé est excellent pour les tâches complexes (IA, PDF), mais il est difficile à exécuter quotidiennement sur un serveur sans maintenance. N8N est parfait pour :

*   **Planification :** Déclencher l'exécution tous les jours à 9h.
*   **Recherche d'Offres :** Utiliser des nœuds N8N pour interroger des API ou des sites web (plus simple que le scraping Python).
*   **Orchestration :** Appeler le cœur de l'agent Python (via un webhook) et envoyer le rapport final par email.

## 2. Architecture de la Solution

Le workflow N8N sera divisé en deux parties principales :

1.  **Le Cœur Python (Service Externe) :** Le code que j'ai développé, responsable de l'optimisation IA et de la génération des documents. Il doit être déployé sur un service Cloud (comme AWS Lambda, Google Cloud Functions, ou un simple serveur web) qui expose un **Webhook HTTP**.
2.  **Le Workflow N8N :** Le planificateur qui déclenche la recherche, appelle le service Python, et gère l'envoi du rapport.

## 3. Préparation du Cœur Python

Le code Python est prêt. Vous devez le déployer sur un service qui peut être appelé par N8N.

**Fichiers Clés à Déployer :**
*   Tout le contenu du dossier `job_application_agent/`
*   Le fichier de configuration `.env` (avec vos clés API et mots de passe)

**Note Importante :** Le déploiement de ce code sur un service Cloud est la seule étape technique. Si vous ne souhaitez pas le faire vous-même, vous devrez faire appel à un prestataire pour cette unique étape.

## 4. Construction du Workflow N8N

Voici les étapes pour construire le workflow dans votre interface N8N :

### Étape 1 : Le Déclencheur (Cron)

Ajoutez un nœud **Cron** pour planifier l'exécution.

| Paramètre | Valeur |
| :--- | :--- |
| **Mode** | `Every Day` |
| **Heure** | `09:00` |

### Étape 2 : Recherche d'Offres (Web Scraper ou API)

C'est la partie la plus variable. Vous pouvez utiliser :

*   **Nœud HTTP Request :** Pour interroger une API de recherche d'emploi (si vous en trouvez une).
*   **Nœud Web Scraper :** Pour extraire des données de pages de résultats simples (ex: APEC, Hellowork).

**Exemple (Simplifié) :** Utilisez un nœud **Web Scraper** pour extraire le titre, l'entreprise, la description et l'URL des 10 premières offres de la page de recherche APEC.

### Étape 3 : Appel du Cœur Python (Webhook HTTP)

C'est le nœud qui va envoyer les offres trouvées à votre service Python pour l'optimisation IA.

Ajoutez un nœud **HTTP Request**.

| Paramètre | Valeur |
| :--- | :--- |
| **Méthode** | `POST` |
| **URL** | `[L'URL du Webhook de votre service Python déployé]` |
| **Body Content** | `JSON` |
| **Body** | `{{ $json.offers }}` (où `offers` est la liste des offres extraites à l'étape 2) |

**Le service Python recevra la liste des offres, les traitera (filtrage, optimisation CV/Lettre, génération PDF) et renverra le rapport HTML et les documents PDF en réponse.**

### Étape 4 : Envoi du Rapport (Email)

Le service Python est conçu pour envoyer l'email directement (via le nœud `EmailSender` que j'ai configuré avec vos identifiants Gmail).

**Alternative N8N :** Si vous préférez que N8N envoie l'email, vous pouvez modifier le cœur Python pour qu'il renvoie le rapport HTML et les chemins des PDF, puis utiliser un nœud **Email Send** dans N8N.

## 5. Kit d'Autonomie Final

Je vous fournis le code source complet de l'agent, corrigé et prêt à être déployé.

**Le bug des liens non cliquables est corrigé :** Les liens dans le rapport HTML sont désormais **relatifs**. Pour qu'ils fonctionnent, vous devez vous assurer que le rapport HTML et les fichiers PDF générés sont toujours dans le **même dossier** sur votre ordinateur.

Je vous livre le kit final dans la prochaine étape.
