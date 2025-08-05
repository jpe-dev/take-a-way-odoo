# Module Init Config

Ce module configure automatiquement Odoo pour la Suisse lors de l'installation initiale.

## Fonctionnalités

- Configure la langue par défaut sur `fr_CH`
- Configure la société principale pour la Suisse (pays: CH, devise: CHF)
- Configure automatiquement le plan comptable suisse après l'installation du module `account`

## Problème identifié

Le module ne fonctionnait pas correctement car :

1. **Erreur de signature** : La fonction `post_init_hook` n'avait pas la bonne signature pour Odoo 18
2. **Ordre de chargement** : Le module se chargeait avant le module `account`, empêchant la configuration du plan comptable
3. **Dépendance incorrecte** : Le module dépendait de `account` mais se chargeait avant lui

## Solutions apportées

### 1. Correction de la signature
```python
# Avant (incorrect pour Odoo 18)
def post_init_hook(cr, registry):

# Après (correct)
def post_init_hook(env):
```

### 2. Suppression de la dépendance à `account`
Le module ne dépend plus de `account` pour éviter les problèmes d'ordre de chargement.

### 3. Configuration différée
La configuration du plan comptable suisse est maintenant effectuée via :
- Un hook post-installation dans le modèle `ResCompany`
- Un script de configuration manuel
- Des paramètres de configuration stockés

## Utilisation

### Installation automatique
Le module se configure automatiquement lors de l'installation d'Odoo.

### Configuration manuelle
Si la configuration automatique échoue, vous pouvez exécuter le script manuel :

```bash
# Depuis le répertoire racine d'Odoo
python3 addons/init_config/test_config.py
```

### Vérification
Pour vérifier que la configuration a fonctionné :

1. Allez dans **Paramètres > Général**
2. Vérifiez que le pays est défini sur "Suisse"
3. Vérifiez que la devise est "CHF"
4. Allez dans **Comptabilité > Configuration > Plan comptable**
5. Vérifiez que le plan comptable suisse est installé

## Ordre de chargement recommandé

Pour que le module fonctionne correctement, l'ordre de chargement dans `docker-compose.yml` doit être :

```yaml
command: >
  --init=base,init_config,account,l10n_ch,base_accounting_kit,take_a_way_loyalty
```

Cela garantit que :
1. `base` se charge en premier
2. `init_config` configure la société
3. `account` installe la comptabilité
4. `l10n_ch` installe la localisation suisse
5. Les autres modules se chargent ensuite 