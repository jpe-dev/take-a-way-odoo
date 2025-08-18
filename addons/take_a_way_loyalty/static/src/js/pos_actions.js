/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { ActionMenu } from "@point_of_sale/app/overrides/components/action_menu/action_menu";

// Patch pour ajouter le champ heure_prevue à l'Order
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

// Patch pour étendre le menu des actions
patch(ActionMenu.prototype, {
    /**
     * Ajoute nos actions personnalisées au menu
     */
    getActionMenuItems() {
        const items = super.getActionMenuItems();
        
        // Ajouter nos actions heure prévue
        const heurePrevueItems = [
            {
                id: 'set_heure_prevue',
                label: 'Définir heure prévue',
                icon: 'fa-clock-o',
                action: () => this.setHeurePrevue(),
            },
            {
                id: 'set_heure_prevue_rapide',
                label: 'Heure prévue +1h',
                icon: 'fa-plus',
                action: () => this.setHeurePrevueRapide(),
            },
            {
                id: 'clear_heure_prevue',
                label: 'Effacer heure prévue',
                icon: 'fa-times',
                action: () => this.clearHeurePrevue(),
            }
        ];
        
        return [...items, ...heurePrevueItems];
    },

    /**
     * Définit l'heure prévue via un popup
     */
    async setHeurePrevue() {
        const { confirmed, payload } = await this.showPopup('InputDialog', {
            title: 'Définir l\'heure prévue',
            body: 'Entrez l\'heure prévue (format: HH:MM)',
            startingValue: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        });
        
        if (confirmed) {
            const [hours, minutes] = payload.split(':').map(Number);
            const heurePrevue = new Date();
            heurePrevue.setHours(hours, minutes, 0, 0);
            
            const order = this.pos.get_order();
            if (order) {
                order.setHeurePrevue(heurePrevue);
                this.showNotification('Heure prévue définie', 3000);
            }
        }
    },

    /**
     * Définit l'heure prévue dans 1 heure
     */
    setHeurePrevueRapide() {
        const order = this.pos.get_order();
        if (order) {
            order.setHeurePrevueRapide();
            this.showNotification('Heure prévue définie dans 1 heure', 3000);
        }
    },

    /**
     * Efface l'heure prévue
     */
    clearHeurePrevue() {
        const order = this.pos.get_order();
        if (order) {
            order.clearHeurePrevue();
            this.showNotification('Heure prévue effacée', 3000);
        }
    },

    /**
     * Affiche une notification
     */
    showNotification(message, duration = 3000) {
        // Utiliser le système de notification d'Odoo
        this.env.services.notification.add(message, {
            type: 'success',
            sticky: false,
        });
    }
}); 