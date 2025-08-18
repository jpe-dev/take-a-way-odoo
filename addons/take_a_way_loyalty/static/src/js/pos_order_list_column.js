/** @odoo-module **/

import { patch } from "@web/core/utils/patch";

// Fonction pour injecter la colonne "Heure prévue" dans le tableau des commandes
function injectHeurePrevueColumn() {
    console.log('[TAKE_A_WAY_LOYALTY] Tentative d\'injection de la colonne Heure prévue...');
    
    // Attendre que le DOM soit chargé
    setTimeout(() => {
        try {
            // Trouver l'en-tête du tableau
            const headerRow = document.querySelector('.header-row');
            if (!headerRow) {
                console.log('[TAKE_A_WAY_LOYALTY] En-tête du tableau non trouvé, nouvelle tentative dans 1s...');
                setTimeout(injectHeurePrevueColumn, 1000);
                return;
            }
            
            // Trouver la colonne "Date"
            const dateColumn = headerRow.querySelector('.col[class*="wide"]:first-child');
            if (!dateColumn) {
                console.log('[TAKE_A_WAY_LOYALTY] Colonne Date non trouvée');
                return;
            }
            
            // Créer la nouvelle colonne "Heure prévue"
            const heurePrevueHeader = document.createElement('div');
            heurePrevueHeader.className = 'col wide p-2';
            heurePrevueHeader.textContent = 'Heure prévue';
            heurePrevueHeader.style.minWidth = '120px';
            
            // Insérer après la colonne Date
            dateColumn.parentNode.insertBefore(heurePrevueHeader, dateColumn.nextSibling);
            
            console.log('[TAKE_A_WAY_LOYALTY] En-tête de colonne Heure prévue ajouté');
            
            // Maintenant ajouter la colonne dans chaque ligne de commande
            injectHeurePrevueInRows();
            
        } catch (error) {
            console.error('[TAKE_A_WAY_LOYALTY] Erreur lors de l\'injection de l\'en-tête:', error);
        }
    }, 500);
}

// Fonction pour injecter la colonne dans chaque ligne de commande
function injectHeurePrevueInRows() {
    try {
        // Trouver toutes les lignes de commande
        const orderRows = document.querySelectorAll('.order-row');
        
        orderRows.forEach((orderRow, index) => {
            // Vérifier si la colonne a déjà été ajoutée
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

// Fonction pour mettre à jour les valeurs d'heure prévue
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

// Observer pour détecter les changements dans le DOM
function setupObserver() {
    try {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    // Vérifier si de nouvelles lignes ont été ajoutées
                    const newOrderRows = document.querySelectorAll('.order-row:not(.heure-prevue-processed)');
                    if (newOrderRows.length > 0) {
                        newOrderRows.forEach(row => row.classList.add('heure-prevue-processed'));
                        injectHeurePrevueInRows();
                    }
                }
            });
        });
        
        // Observer les changements dans le conteneur des commandes
        const ordersContainer = document.querySelector('.orders');
        if (ordersContainer) {
            observer.observe(ordersContainer, { childList: true, subtree: true });
            console.log('[TAKE_A_WAY_LOYALTY] Observer configuré pour détecter les nouvelles commandes');
        }
        
    } catch (error) {
        console.error('[TAKE_A_WAY_LOYALTY] Erreur lors de la configuration de l\'observer:', error);
    }
}

// Fonction principale d'initialisation
function initializeHeurePrevueColumn() {
    console.log('[TAKE_A_WAY_LOYALTY] Initialisation de la colonne Heure prévue...');
    
    // Première injection
    injectHeurePrevueColumn();
    
    // Configurer l'observer pour les nouvelles commandes
    setupObserver();
    
    // Mettre à jour les valeurs toutes les 5 secondes (pour les tests)
    setInterval(updateHeurePrevueValues, 5000);
    
    console.log('[TAKE_A_WAY_LOYALTY] Initialisation terminée');
}

// Démarrer quand le DOM est prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeHeurePrevueColumn);
} else {
    initializeHeurePrevueColumn();
}

// Démarrer aussi quand on navigue dans le PoS
document.addEventListener('DOMContentLoaded', () => {
    // Attendre un peu que le PoS soit complètement chargé
    setTimeout(initializeHeurePrevueColumn, 2000);
});

// Exporter pour compatibilité avec le système de modules Odoo
export { initializeHeurePrevueColumn };
