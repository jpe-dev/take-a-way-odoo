# Module Initial Configuration

Ce module configure automatiquement Odoo pour un environnement suisse en utilisant la localisation fiscale.

## Fonctionnalités

### Configuration automatique via localisation fiscale
- **Pays** : Configure la Suisse comme pays par défaut
- **Devise** : Force l'utilisation du CHF (Franc suisse)
- **Langue** : Configure la langue par défaut sur fr_CH
- **Plan comptable** : Odoo installe automatiquement le plan comptable suisse
- **Taxes TVA** : Odoo configure automatiquement les taux de TVA suisses

### Informations de l'entreprise
- Nom : Take-A-Way
- Adresse : Rue de la Gare 1, 1000 Lausanne
- Téléphone : +41 21 123 45 67
- Email : contact@takeaway.ch

## Principe de fonctionnement

Au lieu de forcer manuellement tous les paramètres, le module utilise l'approche standard d'Odoo :
1. Configure le pays sur la Suisse (`country_id = base.ch`)
2. Configure la devise sur CHF (`currency_id = base.CHF`)
3. Laisse Odoo installer automatiquement le plan comptable et les taxes via la localisation fiscale

Cette approche est plus robuste car elle utilise les mécanismes standards d'Odoo pour la configuration des localisations.

## Installation

Le module est automatiquement installé lors de l'initialisation de la base de données via le docker-compose.yml.

## Configuration

Le module utilise un `post_init_hook` qui s'exécute après l'installation pour :
1. Configurer la langue fr_CH
2. Forcer la localisation fiscale suisse (pays + devise)
3. Déclencher la configuration automatique d'Odoo

## Dépendances

- `base` : Module de base Odoo
- `account` : Module de comptabilité

## Notes

- Le module est configuré avec `auto_install: True` pour s'installer automatiquement
- Les configurations sont appliquées via le fichier `data/res_config_data.xml`
- Le hook post-installation force la localisation fiscale et laisse Odoo faire le reste 