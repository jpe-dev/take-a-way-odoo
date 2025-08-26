/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    /**
     * Définit l'heure prévue de la commande
     */
    setHeurePrevue(heure) {
        this.heure_prevue = heure;
        this.trigger('change');
    },

    /**
     * Efface l'heure prévue de la commande
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
        const heurePrevue = new Date(now.getTime() + 60 * 60 * 1000); // +1 heure
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

// Extension du composant OrderWidget pour afficher l'heure prévue
import { OrderWidget } from "@point_of_sale/app/screens/order/order_widget";
import { Component } from "@odoo/owl";

export class HeurePrevueWidget extends Component {
    setup() {
        super.setup();
    }

    /**
     * Ouvre le popup pour définir l'heure prévue
     */
    openHeurePrevuePopup() {
        this.env.services.popup.add(HeurePrevuePopup, {
            order: this.props.order,
        });
    }

    /**
     * Définit l'heure prévue rapide (+1h)
     */
    setHeurePrevueRapide() {
        this.props.order.setHeurePrevueRapide();
    }

    /**
     * Efface l'heure prévue
     */
    clearHeurePrevue() {
        this.props.order.clearHeurePrevue();
    }
}

HeurePrevueWidget.template = 'take_a_way_loyalty.HeurePrevueWidget';
HeurePrevueWidget.props = {
    order: Object,
};

// Popup pour définir l'heure prévue
export class HeurePrevuePopup extends Component {
    setup() {
        super.setup();
        this.state = {
            heurePrevue: this.props.order.heure_prevue ? new Date(this.props.order.heure_prevue) : new Date(),
            optionRapide: false,
        };
    }

    /**
     * Confirme la définition de l'heure prévue
     */
    confirm() {
        this.props.order.setHeurePrevue(this.state.heurePrevue);
        this.env.services.popup.close();
    }

    /**
     * Annule et ferme le popup
     */
    cancel() {
        this.env.services.popup.close();
    }

    /**
     * Définit l'option rapide
     */
    setOptionRapide(minutes) {
        const now = new Date();
        const heurePrevue = new Date(now.getTime() + minutes * 60 * 1000);
        this.state.heurePrevue = heurePrevue;
        this.state.optionRapide = true;
        this.render();
    }
}

HeurePrevuePopup.template = 'take_a_way_loyalty.HeurePrevuePopup';
HeurePrevuePopup.props = {
    order: Object,
};

// Enregistrement des composants
import { registry } from "@web/core/registry";

registry.category("components").add("HeurePrevueWidget", HeurePrevueWidget);
registry.category("components").add("HeurePrevuePopup", HeurePrevuePopup); 