# Principaux Job Boards en France - 2025

## Job Boards Généralistes

### 1. LinkedIn
- **Audience**: 28 millions de membres en France (11,5 millions actifs en février 2025)
- **Profils**: Tous types de profils (étudiants, cadres, non-cadres)
- **Tarification**: Gratuit + LinkedIn Recruiter (payant)
- **URL**: https://www.linkedin.com
- **Caractéristiques**: 
  - Recherche par filtres avancés
  - Easy Apply disponible
  - Page entreprise pour marque employeur
  - Inbound Marketing

### 2. Indeed
- **Audience**: 7,2 millions de visiteurs uniques/mois (Q3 2024)
- **Profils**: Tous profils (cadres, non-cadres, étudiants, intérim)
- **Tarification**: Gratuit + offre payante (sponsorisation)
- **URL**: https://fr.indeed.com
- **Caractéristiques**: 
  - Plateforme multi-source
  - Paiement au clic pour offres sponsorisées
  - Obligation d'indiquer une fourchette de salaire

### 3. France Travail (ex-Pôle Emploi)
- **Audience**: 5,2 millions d'inscrits (Q3 2024)
- **Profils**: Tous candidats en recherche active
- **Tarification**: Gratuit
- **URL**: https://www.francetravail.fr
- **Caractéristiques**: 
  - Service public de l'emploi
  - Espace entreprise pour recruteurs

### 4. HelloWork (ex-RegionsJob)
- **Audience**: 3 millions de profils en CVthèque
- **Profils**: Tous types de profils
- **Tarification**: Payant (tarifs selon taille entreprise)
- **URL**: https://www.hellowork.com
- **Caractéristiques**: 
  - Fusion RegionsJob + Cadreo
  - Solutions RH adaptées
  - Candidatures qualifiées

### 5. Welcome to the Jungle
- **Audience**: 3+ millions de visiteurs uniques/mois
- **Profils**: Cadres, jeunes diplômés, profils expérimentés (tech, marketing, communication, finance, RH, design)
- **Tarification**: Payant (abonnement annuel avec pack page entreprise)
- **URL**: https://www.welcometothejungle.com
- **Caractéristiques**: 
  - Focus sur marque employeur
  - Contenus visuels (vidéos, interviews, photos)
  - Recherche par valeurs et environnement de travail

### 6. Leboncoin
- **Audience**: 2,2 millions de candidats actifs (2023)
- **Profils**: Tous profils, focus sur chauffeur, livreur, mécanicien, ménage, jobs étudiants
- **Tarification**: Payant pour professionnels
- **URL**: https://www.leboncoin.fr/emploi
- **Caractéristiques**: 
  - Site de petites annonces
  - Possibilité de sponsorisation
  - Espace cadres dédié

### 7. Talent.com (ex-Neuvoo)
- **Profils**: Tous types
- **URL**: https://fr.talent.com
- **Caractéristiques**: Agrégateur d'offres

### 8. Monster
- **URL**: https://www.monster.fr
- **Caractéristiques**: CVthèque importante

### 9. Meteojob
- **URL**: https://www.meteojob.com
- **Caractéristiques**: Job board généraliste

### 10. Jobijoba
- **URL**: https://www.jobijoba.com
- **Caractéristiques**: Agrégateur d'offres

### 11. Keljob
- **URL**: https://www.keljob.com
- **Caractéristiques**: Job board généraliste

### 12. Le Figaro Emploi
- **Audience**: 3,15 millions de visiteurs (décembre 2024)
- **URL**: https://emploi.lefigaro.fr
- **Caractéristiques**: Média traditionnel + emploi

## Job Boards Spécialisés

### Cadres
- **APEC** (Association Pour l'Emploi des Cadres): https://www.apec.fr
- **Cadremploi**: https://www.cadremploi.fr

### Startups/Tech
- **Welcome to the Jungle**: https://www.welcometothejungle.com
- **Choose Your Boss**: https://www.chooseyourboss.com

### Communication & Événementiel
- **Ouest France Emploi**: https://www.ouestfrance-emploi.com
- **RegionsJob** (intégré à HelloWork): sites régionaux (ParisJob, LyonJob, NordJob)

## Job Boards Régionaux (HelloWork Network)
- **ParisJob**: https://www.parisjob.com
- **LyonJob**: https://www.lyonjob.com
- **NordJob**: https://www.nordjob.com
- **Autres sites régionaux** du réseau HelloWork

## Agrégateurs Multi-Sources
1. **Indeed** - Agrège depuis multiple sources
2. **Talent.com** - Agrégateur
3. **Jobijoba** - Agrégateur
4. **Grimp** - Agrège depuis Hellowork, APEC, France Travail, Monster, Ouest France Emploi

## Sites Entreprises - Sections Carrières
Les grandes entreprises ont généralement des pages dédiées au recrutement:
- Format type: `https://www.[entreprise].com/carrieres`
- Format type: `https://www.[entreprise].com/recrutement`
- Format type: `https://www.[entreprise].com/rejoignez-nous`
- Format type: `https://jobs.[entreprise].com`

## Classement par Audience (Décembre 2024)
1. Indeed: 5 475 000 visiteurs
2. Le Figaro Emploi: 3 150 000 visiteurs
3. HelloWork: 3 000 000+ visiteurs

## Notes Techniques pour Scraping/Automation

### Facilité d'accès aux offres
- **Facile**: France Travail, Indeed, HelloWork, Monster, Meteojob
- **Moyen**: LinkedIn (nécessite connexion pour détails), Welcome to the Jungle
- **Difficile**: Sites avec protection anti-bot forte

### APIs Publiques
- La plupart des job boards n'offrent PAS d'API publique gratuite
- LinkedIn: API payante (LinkedIn Recruiter)
- France Travail: API possible mais nécessite inscription
- Indeed: Pas d'API publique officielle

### Méthodes de candidature
1. **Easy Apply** (LinkedIn): formulaire simplifié
2. **Email**: envoi direct avec CV + lettre
3. **Formulaire web**: remplissage de champs + upload documents
4. **Redirection externe**: vers site entreprise ou ATS tiers

### Détection de langue
- Analyser le titre et la description de l'offre
- Mots-clés français: "CDI", "CDD", "poste", "rejoindre", "équipe"
- Mots-clés anglais: "position", "role", "join", "team"
