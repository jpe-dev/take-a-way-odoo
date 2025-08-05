# Missions Cumulables - Documentation

## Vue d'ensemble

La fonctionnalité des **missions cumulables** permet aux utilisateurs de compléter une même mission plusieurs fois, contrairement aux missions non-cumulables qui ne peuvent être complétées qu'une seule fois.

## Fonctionnement

### Missions Cumulables ✅
- **Comportement** : Une fois terminée, la mission est automatiquement réinitialisée
- **État** : Reste en "En cours" après completion
- **Progression** : Remise à zéro pour permettre la répétition
- **Points** : Attribués à chaque completion

### Missions Non-Cumulables ❌
- **Comportement** : Une fois terminée, la mission reste définitivement terminée
- **État** : Passe à "Terminé" après completion
- **Progression** : Conservée pour historique
- **Points** : Attribués une seule fois

## Configuration

### Création d'une mission cumulable

1. **Créer une nouvelle mission**
   - Nom : Nom de la mission
   - Description : Description détaillée
   - Points de récompense : Points attribués à chaque completion
   - Date de début/fin : Période de validité
   - **Cumulable** : ✅ **COCHER** pour activer la répétition

2. **Définir les conditions**
   - Ajouter les conditions spécifiques (achats, parrainage, etc.)
   - Les conditions seront vérifiées à chaque répétition

### Exemple de mission cumulable

```
Nom : Mission Parrainage
Description : Parrainez 2 nouveaux clients
Points de récompense : 100
Cumulable : ✅ Activé
Condition : Parrainage de 2 nouveaux clients
```

## Interface Utilisateur

### Vue des Missions
- **Liste** : Affichage du statut cumulable avec toggle
- **Formulaire** : Case à cocher "Cumulable" dans les détails

### Vue des Participants
- **Bouton "Réinitialiser Mission"** : Visible uniquement pour les missions cumulables terminées
- **Bouton "Vérifier Répétition"** : Affiche le statut de répétition

## Actions Disponibles

### 1. Réinitialisation Manuelle
```python
# Réinitialiser une mission cumulable
participant.action_reinitialiser_mission()
```

### 2. Vérification de Répétition
```python
# Vérifier si une mission peut être répétée
participant.action_verifier_repetition()
```

### 3. Test des Missions Cumulables
```python
# Tester toutes les missions cumulables
mission.test_cumulable_missions()
```

## Logique Technique

### Méthode `_check_mission_completion`
```python
if conditions_remplies and mission_user.etat == 'en_cours':
    # Attribuer les points
    points_record.points_total += mission_user.mission_id.point_recompense
    
    # Gestion cumulable vs non-cumulable
    if mission_user.mission_id.cumulable:
        mission_user._reset_mission_progression()  # Réinitialiser
    else:
        mission_user.etat = 'termine'  # Terminer définitivement
```

### Méthode `_reset_mission_progression`
```python
def _reset_mission_progression(self):
    # Réinitialiser la progression générale
    self.progression = 0
    
    # Réinitialiser les progressions par produit
    for progression_produit in self.progression_par_produit:
        progression_produit.quantite_actuelle = 0
    
    # Réinitialiser les progressions par période
    for progression_periode in self.progression_periode_ids:
        progression_periode.unlink()
    
    # Garder l'état en cours
    self.etat = 'en_cours'
```

## Cas d'Usage

### 1. Mission de Parrainage
- **Objectif** : Parrainer 2 nouveaux clients
- **Cumulable** : ✅ Activé
- **Avantage** : Permet de gagner des points à chaque parrainage

### 2. Mission d'Achat
- **Objectif** : Acheter 5 produits spécifiques
- **Cumulable** : ❌ Désactivé
- **Avantage** : Mission unique pour éviter l'abus

### 3. Mission de Fidélité
- **Objectif** : Effectuer 3 achats dans le mois
- **Cumulable** : ✅ Activé
- **Avantage** : Encourage les achats réguliers

## Tests et Validation

### Test Automatique
```python
# Exécuter le test des missions cumulables
mission.test_cumulable_missions()
```

### Vérification Manuelle
1. Créer une mission cumulable
2. Ajouter un participant
3. Compléter la mission
4. Vérifier que la progression est réinitialisée
5. Compléter à nouveau la mission

## Logs et Debugging

### Logs Informatifs
```
[FIDELITE] Mission cumulable terminée - Réinitialisation pour permettre la répétition
[FIDELITE] Réinitialisation de la progression pour la mission [Nom]
[FIDELITE] Progression réinitialisée pour la mission [Nom]
```

### Logs d'Erreur
```
[FIDELITE] Mission non-cumulable terminée - Passage à l'état terminé
```

## Maintenance

### Vérification Régulière
- Contrôler les missions cumulables vs non-cumulables
- Vérifier la cohérence des points attribués
- Analyser les logs pour détecter les anomalies

### Optimisations Futures
- Ajouter un compteur de completions
- Limiter le nombre de répétitions
- Ajouter des conditions temporelles pour les répétitions 