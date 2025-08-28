/** @odoo-module **/

// Colonne "Heure prévue" dans la liste des commandes PoS (écran de gestion des commandes)

let rootObserver = null;
let listObserver = null;

const RECEIPT_HEADER_HINTS = ['Numéro de reçu', 'Receipt', 'Reçu', 'Order', 'Commande'];

const HEADER_SELECTORS = [
  '.orders .header-row',
  '.header-row',
  'table thead tr',
];

const ROW_SELECTORS = [
  '.orders .order-row',
  '.order-row',
  'table tbody tr',
];

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

function ensureHeaderAfterDate(root) {
  const tr = q1(HEADER_SELECTORS, root);
  if (!tr) return false;
  if (tr.querySelector('.heure-prevue-header')) return true;

  const cells = headerCells(tr);
  if (!cells.length) return false;

  const dateCell = cells[0]; // "Date" est la première
  const tag = dateCell.tagName || 'th';
  const hdr = document.createElement(tag);
  hdr.className = (dateCell.className || '') + ' heure-prevue-header';
  hdr.textContent = 'Heure prévue';
  hdr.style.minWidth = '120px';

  dateCell.parentNode.insertBefore(hdr, dateCell.nextSibling);
  return true;
}

function injectRowCells(root) {
  const rows = qAll(ROW_SELECTORS, root);
  for (const row of rows) {
    if (row.querySelector('.heure-prevue-cell')) continue;
    const cells = rowCells(row);
    if (!cells.length) continue;

    const dateCell = cells[0];
    const tag = dateCell.tagName || 'td';
    const td = document.createElement(tag);
    td.className = (dateCell.className || '') + ' heure-prevue-cell';
    td.style.minWidth = '120px';
    td.innerHTML = '<span class="text-muted">-</span>';

    dateCell.parentNode.insertBefore(td, dateCell.nextSibling);
  }
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

function collectRefs(root) {
  const rows = qAll(ROW_SELECTORS, root);
  const idx = receiptColIndex(root);
  const out = [];
  for (const row of rows) {
    const cells = rowCells(row);
    if (!cells.length) continue;
    const refTxt = (cells[Math.min(idx, cells.length - 1)].textContent || '').replace(/\s+/g, ' ').trim();
    if (refTxt) out.push({ ref: refTxt, row });
  }
  return out;
}

async function fetchHeures(refs) {
  if (!refs.length) return [];
  const uniq = Array.from(new Set(refs.map(r => r.ref)));
  const payload = {
    jsonrpc: '2.0',
    method: 'call',
    params: {
      model: 'pos.order',
      method: 'search_read',
      args: [[['pos_reference', 'in', uniq]], ['pos_reference', 'heure_prevue']],
      kwargs: {},
    },
  };
  try {
    const resp = await fetch('/web/dataset/call_kw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'same-origin',
    });
    const data = await resp.json();
    return (data && data.result) || [];
  } catch (e) {
    console.error('[TAKE_A_WAY_LOYALTY] RPC erreur:', e);
    return [];
  }
}

function fmtHHMM(dtStr) {
  if (!dtStr) return '-';
  const d = new Date(dtStr.replace(' ', 'T') + 'Z'); // UTC -> local
  if (isNaN(d)) return '-';
  return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
}

async function updateValues(root) {
  const pairs = collectRefs(root);
  if (!pairs.length) return;
  const map = new Map();
  for (const { ref, row } of pairs) {
    const cell = row.querySelector('.heure-prevue-cell');
    if (cell) map.set(ref, cell);
  }
  const recs = await fetchHeures(pairs);
  for (const rec of recs) {
    const key = (rec.pos_reference || '').replace(/\s+/g, ' ').trim();
    const cell = map.get(key);
    if (cell) cell.textContent = fmtHHMM(rec.heure_prevue);
  }
}

function injectAll(root) {
  const headerOk = ensureHeaderAfterDate(root);
  injectRowCells(root);
  if (headerOk) updateValues(root);
}

function startListObserver(root) {
  if (listObserver) listObserver.disconnect();
  listObserver = new MutationObserver(() => injectAll(root));
  listObserver.observe(root, { childList: true, subtree: true });
}

function detectAndInjectForOrdersView() {
  const ordersRoot = document.querySelector('.orders');
  if (!ordersRoot) return;

  // Ne pas réinjecter si déjà prêt pour ce conteneur
  if (ordersRoot.dataset.heurePrevueReady === '1') return;

  // Marquer ce conteneur comme initialisé
  ordersRoot.dataset.heurePrevueReady = '1';

  // Injections initiales (et replis avec délais pour les rendus différés)
  setTimeout(() => injectAll(ordersRoot), 0);
  setTimeout(() => injectAll(ordersRoot), 300);
  setTimeout(() => injectAll(ordersRoot), 800);

  // Observer les rafraîchissements de la liste (pagination, filtres, etc.)
  startListObserver(ordersRoot);
}

function init() {
  // Observer la page PoS pour détecter quand la vue .orders apparaît
  if (rootObserver) return;
  rootObserver = new MutationObserver(() => detectAndInjectForOrdersView());
  rootObserver.observe(document.body, { childList: true, subtree: true });

  // Premier essai immédiat (si on arrive déjà sur la vue commandes)
  detectAndInjectForOrdersView();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}