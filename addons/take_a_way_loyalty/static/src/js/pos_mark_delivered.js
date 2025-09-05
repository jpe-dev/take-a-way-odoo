/** @odoo-module **/

// Bootstrap log so we know the asset is loaded
// eslint-disable-next-line no-console
console.info('[TAKE_A_WAY] pos_mark_delivered.js loaded');

async function rpcMarkDelivered(posReference) {
    const body = {
        jsonrpc: '2.0',
        method: 'call',
        params: {
            model: 'pos.order',
            method: 'mark_delivered_by_reference',
            args: [posReference],
            kwargs: {},
        },
    };
    // eslint-disable-next-line no-console
    console.info('[TAKE_A_WAY] RPC mark_delivered_by_reference', body);
    const resp = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'same-origin',
    });
    const data = await resp.json();
    return (data && data.result) || data; // align with other calls
}

function scrapeReferenceFromDom() {
    const side = document.querySelector('.leftpane, .rightpane, .order-container');
    const text = side ? side.textContent : '';
    const match = text && text.match(/\b\d{5}-\d{3}-\d{4}\b/);
    return match ? match[0] : null;
}

// Helpers copied from our column injector to find the selected row's receipt
const RECEIPT_HEADER_HINTS = ['Numéro de reçu', 'Receipt', 'Reçu', 'Order', 'Commande'];
const HEADER_SELECTORS = ['.orders .header-row', '.header-row', 'table thead tr'];
const ROW_SELECTORS = ['.orders .order-row', '.order-row', 'table tbody tr'];

function q1(selectors, root) {
    for (const s of selectors) {
        const el = (root || document).querySelector(s);
        if (el) return el;
    }
    return null;
}

function qAll(selectors, root) {
    for (const s of selectors) {
        const els = (root || document).querySelectorAll(s);
        if (els && els.length) return els;
    }
    return [];
}

function headerCells(tr) {
    if (!tr) return [];
    const ths = tr.querySelectorAll(':scope > th, :scope > [role="columnheader"]');
    if (ths.length) return Array.from(ths);
    return Array.from(tr.children || []);
}

function rowCells(tr) {
    if (!tr) return [];
    const tds = tr.querySelectorAll(':scope > td, :scope > [role="cell"]');
    if (tds.length) return Array.from(tds);
    return Array.from(tr.children || []);
}

function receiptColIndex(root) {
    const tr = q1(HEADER_SELECTORS, root);
    const cells = headerCells(tr);
    if (!cells.length) return 1;
    for (let i = 0; i < cells.length; i++) {
        const t = (cells[i].textContent || '').trim();
        if (t && RECEIPT_HEADER_HINTS.some(h => t.toLowerCase().includes(h.toLowerCase()))) {
            return i;
        }
    }
    return 1;
}

function selectedOrderRow(root) {
    const rows = qAll(ROW_SELECTORS, root);
    if (!rows.length) return null;
    const sel = Array.from(rows).find(r => r.className && /(selected|active|highlight)/i.test(r.className))
        || Array.from(rows).find(r => r.getAttribute('aria-selected') === 'true');
    return sel || rows[0];
}

function posReferenceFromOrdersList() {
    const ordersRoot = document.querySelector('.orders') || document;
    const row = selectedOrderRow(ordersRoot);
    if (!row) return null;
    const idx = receiptColIndex(ordersRoot);
    const cells = rowCells(row);
    if (!cells.length) return null;
    let text = (cells[Math.min(idx, cells.length - 1)].textContent || '').trim();
    // Normalize spaces and remove common prefixes like "Commande"
    text = text.replace(/\s+/g, ' ');
    const m = text.match(/\d{5}-\d{3}-\d{4}/);
    return m ? m[0] : null;
}

function notify(message) {
    // eslint-disable-next-line no-alert
    console.info('[TAKE_A_WAY] notify:', message);
}

// DOM fallback: if the framework override fails, inject a real button next to existing ones
function ensureDomButton() {
    const container = document.querySelector('.pads .control-buttons');
    if (!container) return;
    if (container.querySelector('#pos-mark-delivered')) return; // already present

    const btn = document.createElement('button');
    btn.id = 'pos-mark-delivered';
    btn.className = 'control-button btn btn-light btn-lg lh-lg flex-grow-1 flex-shrink-1';
    btn.innerHTML = '<i class="fa fa-check me-1"></i> Livré';
    btn.addEventListener('click', async () => {
        try {
            // eslint-disable-next-line no-console
            console.info('[TAKE_A_WAY] DOM button clicked');
            let posRef = scrapeReferenceFromDom();
            if (!posRef) posRef = posReferenceFromOrdersList();
            if (!posRef) {
                // eslint-disable-next-line no-console
                console.warn('[TAKE_A_WAY] No reference scraped from DOM');
            }
            const res = await rpcMarkDelivered(posRef);
            // eslint-disable-next-line no-console
            console.info('[TAKE_A_WAY] DOM RPC response', res);
            if (res && res.ok) {
                notify('Commande marquée comme livrée');
            } else {
                notify("Impossible de marquer la commande comme livrée");
            }
        } catch (e) {
            // eslint-disable-next-line no-console
            console.error('[TAKE_A_WAY] DOM button error', e);
        }
    });
    container.appendChild(btn);
    // eslint-disable-next-line no-console
    console.info('[TAKE_A_WAY] Injected DOM Livré button');
}

function startObserverOnceReady() {
    if (!document || !document.body) {
        // Try again when DOM is ready
        document.addEventListener('DOMContentLoaded', startObserverOnceReady, { once: true });
        return;
    }
    if (window.__posDeliveredObserver) return; // avoid duplicates
    const observer = new MutationObserver(() => ensureDomButton());
    observer.observe(document.body, { childList: true, subtree: true });
    window.__posDeliveredObserver = observer;
    ensureDomButton();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserverOnceReady, { once: true });
} else {
    startObserverOnceReady();
}

// Asset ready


