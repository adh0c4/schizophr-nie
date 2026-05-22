# 📁 Structure du dépôt Git — Studio Hackathon
  
> Ce fichier définit l'arborescence attendue, les branches de travail et les règles de commit.

---

## Arborescence attendue

```
studio_XX_nom_du_jeu/
│
├── README_GIT.md          ← ce fichier (ne pas modifier)
├── requirements.txt       ← dépendances Python (au minimum : pygame)
├── .gitignore
│
├── src/                   ← tout le code source Python
│   ├── server.py          ← NE PAS MODIFIER (fourni)
│   ├── network.py         ← NE PAS MODIFIER (fourni — sauf SERVER_IP)
│   ├── gamestate.py       ← ⭐ logique de jeu commune (conçue ensemble J1)
│   ├── client_j1.py       ← ⭐ vue Joueur 1 — Chapitre 1 (Binôme A) + Chapitre 2 (Binôme B)
│   ├── client_j2.py       ← ⭐ vue Joueur 2 — Chapitre 1 (Binôme A) + Chapitre 2 (Binôme B)
│   └── check_network.py   ← outil diagnostic (fourni)
│
├── tests/                 ← tests unitaires
│   ├── test_gamestate.py  ← tests sur GameState (obligatoire)
│   └── test_*.py          ← autres classes testées
│
├── ressources/            ← images, sons, polices
│   ├── images/
│   └── sons/
│
└── docs/                  ← livrables documentaires
    ├── DiagrammeClasse_J1.pdf
    ├── CasUtilisation_J1.pdf
    ├── Sequence_Action_J3.pdf
    ├── Sequence_Victoire_J3.pdf
    ├── GuideTechnique_J5.pdf
    └── GuideUtilisateur_J5.pdf
```

---

## Qui fait quoi

Les deux joueurs (Joueur 1 et Joueur 2) sont **présents dans les deux chapitres**. Les binômes ne sont pas affectés à un joueur — ils sont affectés à un **chapitre**.

| Rôle | Responsabilité | Fichiers principaux |
|------|---------------|---------------------|
| **Lead BA2** | Architecture, Git, GitHub Project, synchro | `gamestate.py` (supervision), tableau Kanban dans GitHub Project |
| **Binôme A** | Toutes les mécaniques du **Chapitre 1** — actions J1 et J2 pour ce chapitre | `src/client_j1.py` (section chap 1), `src/client_j2.py` (section chap 1), `src/gamestate.py` (clés chap 1) |
| **Binôme B** | Toutes les mécaniques du **Chapitre 2** — actions J1 et J2 pour ce chapitre | `src/client_j1.py` (section chap 2), `src/client_j2.py` (section chap 2), `src/gamestate.py` (clés chap 2) |
| **Tout le studio** | GameState commun (Jour 1), intégration (Jour 4), tests, docs | `gamestate.py`, `tests/`, `docs/` |

> **Règle d'or pour éviter les conflits** : chaque binôme travaille dans des **fonctions nommées** distinctement dans les clients — ex. `draw_chapitre1()` et `draw_chapitre2()`. Jamais deux personnes ne modifient la même fonction en même temps.

---

## Structure des branches Git — Workflow GitHub

```
main          ← version stable, démo finale
  ├── feature/featureA   ← Binôme A travaille ici (J2–J3), fusionné via Pull Request
  └── feature/featureB   ← Binôme B travaille ici (J2–J3), fusionné via Pull Request
```

> Les branches `feature/` sont créées depuis `main` et fusionnées dans `main` **via Pull Request** sur GitHub.

### Flux de travail jour par jour

| Jour | Action Git & GitHub |
|------|---------------------|
| **J1** | Tout le monde travaille directement sur `main` — GameState commun, structure de base |
| **J2 matin** | Créer `feature/featureA` et `feature/featureB` depuis `main`. Créer les Issues correspondantes dans GitHub Project |
| **J2–J3** | Chaque binôme commit sur sa branche. Synchronisation avec le dépôt distant toutes les 2h |
| **J4 matin** | Ouvrir une **Pull Request** pour chaque branche → revue par le Lead → merge dans `main` |
| **J4 après-midi** | Tests end-to-end sur `main`, puis corrections en créant `fix/fixA` et `fix/fixB` depuis `main` |
| **J4 soir** | `main` est la version finale — tag `v1.0.0` |

### Commandes de fusion (Jour 4 — via Pull Request GitHub)

Le merge ne se fait **pas en ligne de commande** mais via l'interface GitHub :

1. Aller sur le dépôt GitHub → onglet **Pull requests**
2. Ouvrir la PR `feature/AAA` → `main`
3. Le Lead effectue la revue et résout les conflits si nécessaire
4. Cliquer sur **Merge pull request**
5. Répéter pour `feature/BBB`

En cas de conflit, les résoudre localement puis pousser. 
Après les deux merges, créer le tag de version finale.

---

## Tableau Kanban — GitHub Project

Le suivi des tâches se fait via le **tableau Kanban du GitHub Project** associé au dépôt.

### Mise en place (Jour 1 — Lead)

1. Aller sur le dépôt GitHub → onglet **Projects**
2. Cliquer sur **New project** → choisir le template **Team planning**
3. Nommer le projet : `Studio XX — Nom du Jeu`
4. Configurer les **3 colonnes** suivantes :

| Colonne | Contenu |
|---------|---------|
| **Todo** | Tâches qui concernent tout le studio (intégration, tests globaux, livrables docs) |
| **In Progress** | Ce sur quoi tout le studio travaille ensemble à cet instant |
| **Done** | Tâches complètes  |

### Utilisation des Issues GitHub

Chaque tâche du tableau est une **Issue GitHub** :

1. Onglet **Issues** → **New issue**
2. Renseigner :
   - **Titre** : description courte de la tâche (ex. `Séquence leviers côté serveur`)
   - **Assignees** : prénom(s) du ou des membres responsables
   - **Labels** : `chapitre-1`, `chapitre-2`, ou `commun` (créer ces labels au Jour 1)
   - **Project** : sélectionner le projet Kanban du studio
3. L'Issue apparaît automatiquement dans la colonne **Todo** — la déplacer dans la bonne colonne

### Lier commits et Pull Requests aux Issues

Pour qu'une Issue se ferme automatiquement lors du merge d'une PR, utiliser les **mots-clés GitHub** dans le message de commit ou la description de PR :

```
fix(chap1): collision valve grippée — closes #12
feat(chap2): affichage score joueur 2 — closes #15
```

Mots-clés acceptés : `closes`, `fixes`, `resolves` (suivi du numéro d'Issue avec `#`).

### Règles du tableau

- **Maximum 3 cartes par colonne "En cours"** — au-delà, le studio est dispersé
- **Chaque carte est assignée** — toujours au moins un membre responsable


---

## Convention de nommage des commits

```
type(scope): description courte en minuscules
```

| Type | Scope | Exemple |
|------|-------|---------|
| `feat` | `chap1` ou `chap2` ou `commun` | `feat(chap1): séquence leviers côté serveur` |
| `fix` | `chap1` ou `chap2` | `fix(chap2): collision valve grippée — closes #12` |
| `test` | `gamestate` ou `chap1`... | `test(gamestate): cas limite timer à 0` |
| `docs` | livrable | `docs: diagramme séquence victoire J3` |
| `merge` | — | `merge: synchronisation main dans feature/chapitre-1` |
| `refactor` | scope | `refactor(chap1): factoriser apply_action levier` |

### Règles obligatoires

1. **Commit au minimum 2 fois par jour** par binôme — matin et fin d'après-midi
2. **Ne jamais commiter `__pycache__/`** ni les fichiers `.pyc`
3. **Référencer l'Issue** dans le message de commit quand c'est pertinent (`closes #N`)

---

## `.gitignore` minimal

```
__pycache__/
*.pyc
*.pyo
.DS_Store
Thumbs.db
*.log
```

---

## Démarrage Jour 1 — checklist Git & GitHub

```bash
# 1. Cloner le dépôt vide fourni par le prof
git clone https://<url_fournie_par_le_prof> studio_XX_nom_du_jeu
cd studio_XX_nom_du_jeu

# 2. Créer la structure
mkdir src tests ressources docs ressources/images ressources/sons

# 3. Copier la boite à outils dans src/
cp -r /chemin/boite_outils/* src/

# 4. Fichiers de base
touch requirements.txt .gitignore
echo "pygame" > requirements.txt

# 5. Premier commit sur main
git add .
git commit -m "feat(commun): initialisation structure studio"
git push -u origin main

# 6. Créer les branches chapitre (Jour 2 matin seulement)
# git checkout -b feature/featureA   ← Binôme A fait ça le Jour 2
# git checkout -b feature/featureB   ← Binôme B fait ça le Jour 2
```

### Checklist GitHub Project (Lead — Jour 1)

- [ ] Créer le **Project** Kanban sur GitHub avec les 3 colonnes
- [ ] Créer les **labels** : `chapitre-1`, `chapitre-2`, `commun`
- [ ] Créer les premières **Issues** pour les tâches du Jour 1 et les assigner

---

## Commandes utiles rappel

```bash
git status                          # état du dépôt
git add .                           # ajouter tous les fichiers modifiés
git commit -m "feat(chap1): ..."    # commiter
git push                            # envoyer sur le serveur
git log --oneline                   # historique compact
git pull origin main                # récupérer les dernières modifs de main
git merge main                      # synchroniser main dans la branche courante
```

---

*HEH — Département Sciences & Techniques — Hackathon Python*
