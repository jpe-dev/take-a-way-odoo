#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour exécuter le test de disponibilité des produits dans le PoS
"""

import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_disponibilite_pos import test_disponibilite_pos

if __name__ == "__main__":
    print("=== Démarrage du test de disponibilité des produits dans le PoS ===")
    test_disponibilite_pos()
    print("=== Test terminé ===") 