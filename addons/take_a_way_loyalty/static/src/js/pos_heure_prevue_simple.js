/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

// Patch simple pour ajouter le champ heure_prevue à l'Order
patch(Order.prototype, {
    setup() {
        super.setup();
        this.heure_prevue = null;
    },

    /**
     * Définit l'heure prévue
     */
    setHeurePrevue(heure) {
        this.heure_prevue = heure;
        this.trigger('change');
    },

    /**
     * Efface l'heure prévue
     */
    clearHeurePrevue() {
        this.heure_prevue = null;
        this.trigger('change');
    },

    /**
     * Définit l'heure prévue dans 1 heure
     */
    setHeurePrevueRapide() {
        const now = new Date();
        const heurePrevue = new Date(now.getTime() + 60 * 60 * 1000);
        this.setHeurePrevue(heurePrevue);
    },

    /**
     * Obtient l'heure prévue formatée
     */
    getHeurePrevueFormatted() {
        if (!this.heure_prevue) return '';
        const date = new Date(this.heure_prevue);
        return date.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}); 