#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer les actions via l'API REST d'Odoo
"""

import requests
import json

def create_actions_via_api():
    """Crée les actions via l'API REST"""
    
    # Configuration
    base_url = "http://localhost:8069"
    db = "db-odoo-ta"
    username = "admin"
    password = "admin"  # Changez si nécessaire
    
    # Authentification
    auth_url = f"{base_url}/web/session/authenticate"
    auth_data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": db,
            "login": username,
            "password": password
        },
        "id": 1
    }
    
    session = requests.Session()
    
    try:
        # Authentification
        response = session.post(auth_url, json=auth_data)
        if response.status_code != 200:
            print(f"❌ Erreur d'authentification: {response.status_code}")
            return False
        
        # Créer les actions
        actions_data = [
            {
                "name": "Définir heure prévue",
                "model_id": "pos.order",
                "state": "code",
                "code": "if records:\n    records.action_set_heure_prevue()",
                "binding_model_id": "pos.order",
                "binding_view_types": "form"
            },
            {
                "name": "Heure prévue +1h",
                "model_id": "pos.order",
                "state": "code",
                "code": "if records:\n    records.action_set_heure_prevue_rapide()",
                "binding_model_id": "pos.order",
                "binding_view_types": "form"
            },
            {
                "name": "Effacer heure prévue",
                "model_id": "pos.order",
                "state": "code",
                "code": "if records:\n    records.action_clear_heure_prevue()",
                "binding_model_id": "pos.order",
                "binding_view_types": "form"
            }
        ]
        
        print("=== Création des actions via API ===")
        
        for i, action_data in enumerate(actions_data, 1):
            create_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "ir.actions.server",
                    "method": "create",
                    "args": [action_data]
                },
                "id": i
            }
            
            response = session.post(f"{base_url}/web/dataset/call_kw", json=create_data)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    print(f"✅ Action '{action_data['name']}' créée (ID: {result['result']})")
                else:
                    print(f"❌ Erreur création action '{action_data['name']}': {result}")
            else:
                print(f"❌ Erreur HTTP pour action '{action_data['name']}': {response.status_code}")
        
        print("")
        print("🎉 Script terminé!")
        print("")
        print("📋 Instructions:")
        print("1. Allez dans Point de Vente > Commandes")
        print("2. Sélectionnez une commande")
        print("3. Cliquez sur Actions dans la barre d'outils")
        print("4. Vous devriez voir les actions heure prévue")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_actions_via_api()
    
    if success:
        print("✅ Script terminé avec succès!")
    else:
        print("❌ Script échoué!") 