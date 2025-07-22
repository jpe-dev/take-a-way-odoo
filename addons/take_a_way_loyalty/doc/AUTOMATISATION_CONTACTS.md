# Automatisation des Contacts - Module de Fidélité

## Vue d'ensemble

Cette fonctionnalité permet d'ajouter automatiquement les nouveaux contacts créés dans Odoo à toutes les missions de fidélité actives.

## Fonctionnalités

### Ajout Automatique des Nouveaux Contacts

**Comment ça marche :**
- Lorsqu'un nouveau contact (non-entreprise) est créé dans Odoo
- Le système vérifie automatiquement toutes les missions actives
- Le contact est ajouté comme participant à chaque mission active
- Un enregistrement de points de fidélité est créé automatiquement si nécessaire

**Critères d'ajout automatique :**
- Le contact doit être de type "contact" (pas une entreprise)
- Le contact ne doit pas déjà être participant à la mission
- La mission doit être active (date de début ≤ aujourd'hui ≤ date de fin)

## Utilisation

L'automatisation fonctionne en arrière-plan. Aucune action manuelle n'est requise.

## Logs

Toutes les actions sont enregistrées dans les logs Odoo avec le préfixe `[FIDELITE]` :
- Création de nouveaux contacts
- Ajout automatique aux missions
- Erreurs éventuelles

## Configuration

Aucune configuration supplémentaire n'est requise. L'automatisation est activée par défaut.

## Dépannage

### Vérifier les logs
```bash
# Dans les logs Odoo, rechercher :
[FIDELITE] Nouveau contact créé
[FIDELITE] Missions actives trouvées
[FIDELITE] Contact ajouté automatiquement
```

### Vérifier manuellement
1. Créer un nouveau contact
2. Vérifier dans les missions actives si le contact apparaît dans la liste des participants
3. Vérifier que l'enregistrement de points a été créé

## Notes Techniques

- L'automatisation utilise la méthode `create` du modèle `res.partner`
- Les vérifications de doublons sont effectuées avant chaque ajout
- Les erreurs sont gérées gracieusement avec des logs détaillés
- La création des enregistrements de points est automatique 