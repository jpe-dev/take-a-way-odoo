/** @odoo-module **/

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";

// Chargement des assets pour le PoS
registry.category("assets").add("take_a_way_loyalty.pos_assets", {
    js: [
        "/take_a_way_loyalty/static/src/js/pos_heure_prevue.js",
    ],
    css: [
        "/take_a_way_loyalty/static/src/css/pos_heure_prevue.css",
    ],
    xml: [
        "/take_a_way_loyalty/static/src/xml/pos_heure_prevue.xml",
    ],
}); 