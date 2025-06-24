# 🔐 Partage de Secret de Shamir

Application moderne pour créer et récupérer des secrets partagés en utilisant l'algorithme de partage de secret de Shamir.

## ✨ Fonctionnalités

- **Interface web moderne** (recommandée) - Fonctionne dans votre navigateur
- **Interface graphique Tkinter** (si disponible)
- **Mode création** : Partagez n'importe quel secret en plusieurs parts
- **Mode récupération** : Reconstituez un secret à partir des parts
- **Copier-coller intégré** pour faciliter la gestion des parts
- **Interface en ligne de commande** (mode legacy)
- **Validation robuste** des entrées
- **Code de qualité** respectant les bonnes pratiques Python

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation rapide
```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install pyperclip
```

### Installation complète avec fichier requirements.txt
```bash
pip install -r requirements.txt
```

## 💻 Utilisation

### Interface Web (Recommandée)
```bash
python3 main.py --web
```
✅ **Avantages** : Fonctionne sur tous les systèmes, interface moderne, pas de dépendances graphiques
- L'interface s'ouvre automatiquement dans votre navigateur
- Accessible via http://localhost:8080

### Interface Graphique Tkinter
```bash
python3 main.py
```
⚠️ **Note** : Nécessite Tkinter installé. Si non disponible, utilisez l'interface web.

### Interface en Ligne de Commande
```bash
python3 main.py --cli
```

## 📱 Guide d'utilisation des interfaces

### Mode Création
1. **Entrez votre secret** : N'importe quel texte (phrase de récupération, mot de passe, note, etc.)
   - ✅ Exemple : `abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about`
   - ✅ Exemple : `Mon mot de passe super secret 123!`
   - ✅ Supporte tous les caractères UTF-8 (émojis, accents, etc.)

2. **Configurez les paramètres** :
   - **Nombre total de parts (n)** : Entre 2 et 20
   - **Parts minimum (k)** : Entre 2 et n

3. **Récupérez les parts** et stockez-les séparément

### Mode Récupération
1. **Entrez les parts** au format correct (voir section suivante)
2. **Une part par ligne**
3. **Minimum k parts** nécessaires

## 📋 Format des Parts

### Format correct
```
index:valeur1,valeur2,valeur3,...
```

### Exemples réels de parts
```
1:109,97,32,112,104,114,97,115,101,32,115,101,99,114,195,168,116,101
2:218,194,64,224,208,228,194,230,202,64,230,202,226,228,134,136,234
3:71,35,96,80,56,86,35,89,47,96,89,47,83,86,197,200,107,47,96,92
```

### ❌ Formats incorrects à éviter
```
❌ Part 1: [109,97,32,112...]     # Pas de "Part" ni de crochets
❌ 1:[109,97,32,112...]           # Pas de crochets
❌ 1: 109,97,32,112...            # Pas d'espace après ":"
```

### ✅ Comment saisir les parts
1. **Interface web/graphique** : Copiez-collez directement depuis les résultats
2. **Mode CLI** : Tapez manuellement au format `index:val1,val2,...`

## 🔧 Paramètres détaillés

### Nombre total de parts (n)
- **Minimum** : 2 parts
- **Maximum** : 20 parts (limitation de l'interface)
- **Recommandé** : 3-7 parts pour un usage personnel

### Parts minimum pour reconstituer (k)
- **Minimum** : 2 parts
- **Maximum** : n (nombre total)
- **Recommandé** : n-1 ou n-2 pour plus de sécurité

### Exemples de configurations
| Configuration | Description | Cas d'usage |
|---------------|-------------|-------------|
| n=3, k=2 | 3 parts, 2 nécessaires | Usage simple, tolérance à 1 perte |
| n=5, k=3 | 5 parts, 3 nécessaires | Usage familial, tolérance à 2 pertes |
| n=7, k=4 | 7 parts, 4 nécessaires | Usage professionnel, haute sécurité |

## 🛡️ Sécurité et bonnes pratiques

### Stockage des parts
- ✅ **Stockez chaque part dans un endroit différent**
- ✅ Utilisez des supports différents (cloud, papier, clé USB)
- ✅ Donnez des parts à des personnes de confiance
- ❌ Ne stockez jamais toutes les parts au même endroit

### Types de secrets supportés
- ✅ **Phrases de récupération** crypto (12, 24 mots)
- ✅ **Mots de passe** complexes
- ✅ **Clés privées** ou graines
- ✅ **Notes sensibles** ou codes PIN
- ✅ **Tous caractères UTF-8** (accents, émojis, langues étrangères)

### Limitations importantes
- ⚠️ **Pas de chiffrement supplémentaire** : les parts contiennent le secret
- ⚠️ **k parts suffisent** : Si quelqu'un obtient k parts, il peut reconstituer le secret
- ⚠️ **Pas de récupération partielle** : Il faut exactement k parts minimum

## 🏗️ Architecture du projet

```
shamir-secret-sharing/
├── main.py              # Point d'entrée principal avec options
├── shamir_core.py       # Logique métier (algorithme de Shamir)
├── gui.py              # Interface graphique Tkinter
├── web_gui.py          # Interface web (serveur HTTP intégré)
├── requirements.txt     # Dépendances Python
├── .gitignore          # Fichiers à ignorer par Git
└── README.md           # Documentation
```

## 🧪 Exemple complet d'utilisation

### 1. Création d'un secret
**Secret d'entrée** :
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
```

**Configuration** : 5 parts total, 3 minimum

**Parts générées** :
```
1:97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,111,117,116
2:194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,234,234
3:35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,91,91
```

### 2. Récupération du secret
**Parts utilisées** (n'importe quelles 3 parts) :
```
1:97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,97,110,100,111,110,32,97,98,111,117,116
3:35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,35,74,44,77,74,96,35,38,91,91
2:194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,194,220,200,222,220,64,194,196,234,234
```

**Secret récupéré** :
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
```

## 🐛 Dépannage

### Tkinter non disponible
```bash
# macOS avec Homebrew
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk

# Alternative : Utilisez l'interface web
python3 main.py --web
```

### Problème de port (interface web)
```bash
# Si le port 8080 est occupé, l'application vous l'indiquera
# Fermez l'autre application ou redémarrez
```

### Erreur de format de parts
- ✅ Vérifiez qu'il n'y a **pas d'espaces** après les `:`
- ✅ Utilisez des **virgules** (pas d'espaces) entre les nombres
- ✅ **Une part par ligne**
- ✅ Copiez-collez directement depuis l'application

### Problème de copier-coller
```bash
# Linux : installer xclip ou xsel
sudo apt-get install xclip

# Alternative : copiez manuellement le texte
```

## 🔬 Algorithme de Shamir

L'algorithme de partage de secret de Shamir utilise :
- **Interpolation de Lagrange** sur un corps fini GF(257)
- **Polynômes aléatoires** de degré k-1
- **Seuil configurable** (k parmi n)
- **Sécurité cryptographique** : impossible de reconstituer le secret avec moins de k parts
- **Perfect secrecy** : k-1 parts ne révèlent aucune information sur le secret