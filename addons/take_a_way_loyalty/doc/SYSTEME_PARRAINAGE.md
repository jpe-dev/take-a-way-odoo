# Système de Parrainage - Take A Way Loyalty

## Vue d'ensemble

Le système de parrainage permet aux clients existants de parrainer de nouveaux clients et de gagner des points de fidélité en récompense.

## Fonctionnalités

### 1. Génération automatique de codes de parrainage

- Chaque contact (non-entreprise) reçoit automatiquement un code de parrainage unique de 6 chiffres lors de sa création
- Le code est généré automatiquement et est unique dans le système
- Les codes existants sont préservés lors des mises à jour

### 2. Interface utilisateur

#### Formulaire de contact
- Nouvel onglet "Parrainage" dans le formulaire des contacts
- Affichage du code de parrainage du contact (lecture seule)
- Champ pour définir le parrain du contact
- Liste des filleuls (contacts parrainés)
- Bouton pour saisir un code de parrainage

#### Wizard de saisie de code
- Interface dédiée pour saisir un code de parrainage
- Validation du code saisi
- Messages d'erreur appropriés

### 3. Missions de parrainage

#### Création d'une mission
1. Créer une nouvelle mission
2. Ajouter une condition de type "Parrainage d'un nouveau client"
3. Définir le nombre de filleuls requis (quantité)
4. Définir les points de récompense

#### Vérification automatique
- Le système vérifie automatiquement le nombre de filleuls actifs
- Un filleul est considéré comme "actif" s'il a fait au moins une commande depuis le début de la mission
- La progression est mise à jour en temps réel
- Les points sont attribués automatiquement quand la condition est remplie

## Utilisation

### Pour un client existant (parrain)

1. **Consulter son code de parrainage**
   - Aller dans Contacts > Sélectionner le contact
   - Onglet "Parrainage" > Code de parrainage

2. **Partager son code**
   - Communiquer le code de parrainage aux nouveaux clients

### Pour un nouveau client (filleul)

1. **Créer le contact**
   - Créer un nouveau contact dans Odoo

2. **Saisir le code de parrainage**
   - Dans le formulaire du contact, cliquer sur "Saisir un code de parrainage"
   - Entrer le code du parrain
   - Valider

3. **Vérification**
   - Le parrain est automatiquement défini
   - Le contact apparaît dans la liste des filleuls du parrain

### Pour créer une mission de parrainage

1. **Créer la mission**
   - Aller dans Fidélité > Missions
   - Créer une nouvelle mission

2. **Ajouter la condition**
   - Dans l'onglet "Conditions"
   - Type de condition : "Parrainage d'un nouveau client"
   - Quantité : nombre de filleuls requis

3. **Ajouter les participants**
   - Utiliser "Ajouter tous les contacts" ou ajouter manuellement

## Structure technique

### Modèles

#### res.partner (étendu)
- `code_parrainage` : Code unique de 6 chiffres
- `parrain_id` : Référence vers le contact parrain
- `filleuls_ids` : Liste des contacts parrainés
- `nombre_filleuls` : Nombre de filleuls (calculé)

#### take_a_way_loyalty.condition_mission
- Support du type "PARRAINAGE"
- Utilise le champ `quantite` pour définir le nombre de filleuls requis

### Vérification des missions

La méthode `_check_parrainage_condition` dans `PosOrder` :
1. Récupère tous les filleuls du participant
2. Vérifie si chaque filleul a fait au moins une commande depuis le début de la mission
3. Met à jour la progression
4. Vérifie si la condition est remplie

## Migration

Lors de la mise à jour du module :
1. Le hook `post_init_hook` est exécuté
2. Tous les contacts existants reçoivent un code de parrainage
3. Les codes existants sont préservés

## Exemple de mission

```xml
<record id="mission_parrainage" model="take_a_way_loyalty.mission">
    <field name="name">Parrainez 2 nouveaux clients</field>
    <field name="description">Gagnez 100 points en parrainant 2 nouveaux clients</field>
    <field name="point_recompense">100</field>
    <field name="debut">2024-01-01</field>
    <field name="fin">2024-12-31</field>
</record>

<record id="condition_parrainage" model="take_a_way_loyalty.condition_mission">
    <field name="mission_id" ref="mission_parrainage"/>
    <field name="type_condition" ref="type_mission_parrainage"/>
    <field name="quantite">2</field>
</record>
```

## Sécurité

- Seuls les utilisateurs avec les droits appropriés peuvent modifier les parrainages
- Les codes de parrainage sont uniques (contrainte SQL)
- Validation des codes saisis
- Protection contre l'auto-parrainage 