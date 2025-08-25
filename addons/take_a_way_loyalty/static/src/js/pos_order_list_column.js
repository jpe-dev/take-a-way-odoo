/** @odoo-module **/

import { patch } from "@web/core/utils/patch";

// Variable pour éviter l'exécution multiple
let isInitialized = false;

// Fonction pour injecter la colonne "Heure prévue" dans le tableau des commandes
function injectHeurePrevueColumn() {
    if (isInitialized) {
        console.log('[TAKE_A_WAY_LOYALTY] Déjà initialisé, sortie...');
        return;
    }
    
    console.log('[TAKE_A_WAY_LOYALTY] Injection de la colonne Heure prévue...');
    
    try {
        // Trouver TOUS les en-têtes de tableaux
        const headerRows = document.querySelectorAll('.header-row');
        console.log(`[TAKE_A_WAY_LOYALTY] Trouvé ${headerRows.length} en-têtes de tableaux`);
        
        headerRows.forEach((headerRow, headerIndex) => {
            // Vérifier si la colonne a déjà été ajoutée dans cet en-tête
            if (headerRow.querySelector('.heure-prevue-header')) {
                console.log(`[TAKE_A_WAY_LOYALTY] En-tête ${headerIndex} déjà traité`);
                return;
            }
            
            // Trouver la colonne "Date" (première colonne wide)
            const dateColumn = headerRow.querySelector('.col[class*="wide"]:first-child');
            if (!dateColumn) {
                console.log(`[TAKE_A_WAY_LOYALTY] Colonne Date non trouvée dans l'en-tête ${headerIndex}`);
                return;
            }
            
            // Créer la nouvelle colonne "Heure prévue"
            const heurePrevueHeader = document.createElement('div');
            heurePrevueHeader.className = 'col wide p-2 heure-prevue-header';
            heurePrevueHeader.textContent = 'Heure prévue';
            heurePrevueHeader.style.minWidth = '120px';
            
            // Insérer après la colonne Date
            dateColumn.parentNode.insertBefore(heurePrevueHeader, dateColumn.nextSibling);
            
            console.log(`[TAKE_A_WAY_LOYALTY] En-tête de colonne Heure prévue ajouté dans l'en-tête ${headerIndex}`);
        });
        
        // Maintenant ajouter la colonne dans TOUTES les lignes de commande
        injectHeurePrevueInAllRows();
        
        // Marquer comme initialisé
        isInitialized = true;
        console.log('[TAKE_A_WAY_LOYALTY] Initialisation terminée avec succès');
        
    } catch (error) {
        console.error('[TAKE_A_WAY_LOYALTY] Erreur lors de l\'injection:', error);
    }
}

// Fonction pour injecter la colonne dans TOUTES les lignes de commande
function injectHeurePrevueInAllRows() {
    try {
        // Trouver TOUTES les lignes de commande (tous les tableaux)
        const orderRows = document.querySelectorAll('.order-row');
        console.log(`[TAKE_A_WAY_LOYALTY] Trouvé ${orderRows.length} lignes de commandes à traiter`);
        
        orderRows.forEach((orderRow, rowIndex) => {
            // Vérifier si la colonne a déjà été ajoutée dans cette ligne
            if (orderRow.querySelector('.heure-prevue-cell')) {
                return;
            }
            
            // Trouver la première colonne (Date)
            const firstColumn = orderRow.querySelector('.col:first-child');
            if (!firstColumn) return;
            
            // Créer la cellule "Heure prévue"
            const heurePrevueCell = document.createElement('div');
            heurePrevueCell.className = 'col wide p-2 heure-prevue-cell';
            heurePrevueCell.style.minWidth = '120px';
            
            // Pour l'instant, afficher un placeholder
            // Plus tard, on récupérera la vraie valeur depuis l'API
            heurePrevueCell.innerHTML = '<div class="text-muted">-</div>';
            
            // Insérer après la première colonne
            firstColumn.parentNode.insertBefore(heurePrevueCell, firstColumn.nextSibling);
        });
        
        console.log(`[TAKE_A_WAY_LOYALTY] Colonne Heure prévue ajoutée dans ${orderRows.length} lignes`);
        
    } catch (error) {
        console.error('[TAKE_A_WAY_LOYALTY] Erreur lors de l\'injection dans les lignes:', error);
    }
}

// Fonction pour mettre à jour les valeurs d'heure prévue (une seule fois)
function updateHeurePrevueValues() {
    try {
        // Ici on pourrait faire un appel API pour récupérer les heures prévues
        // Pour l'instant, on affiche des valeurs de test
        const heurePrevueCells = document.querySelectorAll('.heure-prevue-cell');
        
        heurePrevueCells.forEach((cell, index) => {
            // Simuler une heure prévue (à remplacer par la vraie logique)
            const now = new Date();
            const heurePrevue = new Date(now.getTime() + (index + 1) * 30 * 60 * 1000); // +30min, +1h, +1h30...
            
            const hours = heurePrevue.getHours().toString().padStart(2, '0');
            const minutes = heurePrevue.getMinutes().toString().padStart(2, '0');
            
            cell.innerHTML = `<div class="heure-prevue-value">${hours}:${minutes}</div>`;
        });
        
        console.log('[TAKE_A_WAY_LOYALTY] Valeurs d\'heure prévue mises à jour');
        
    } catch (error) {
        console.error('[TAKE_A_WAY_LOYALTY] Erreur lors de la mise à jour des valeurs:', error);
    }
}

// Fonction principale d'initialisation (une seule fois)
function initializeHeurePrevueColumn() {
    if (isInitialized) {
        console.log('[TAKE_A_WAY_LOYALTY] Déjà initialisé, sortie...');
        return;
    }
    
    console.log('[TAKE_A_WAY_LOYALTY] Initialisation de la colonne Heure prévue...');
    
    // Attendre un peu que le DOM soit complètement chargé
    setTimeout(() => {
        injectHeurePrevueColumn();
        
        // Mettre à jour les valeurs une seule fois après l'injection
        setTimeout(updateHeurePrevueValues, 1000);
        
    }, 1000);
    
    console.log('[TAKE_A_WAY_LOYALTY] Initialisation programmée');
}

// Démarrer quand le DOM est prêt (une seule fois)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeHeurePrevueColumn);
} else {
    initializeHeurePrevueColumn();
}

// Démarrer aussi quand on navigue dans le PoS (une seule fois par page)
document.addEventListener('DOMContentLoaded', () => {
    // Attendre un peu que le PoS soit complètement chargé
    setTimeout(initializeHeurePrevueColumn, 2000);
});

// Exporter pour compatibilité avec le système de modules Odoo
export { initializeHeurePrevueColumn };

