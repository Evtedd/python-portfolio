/*
 * NOIR MAISON HAUTE server side product catalog
 * Prices MUST match src/catalog.js. Server is the source of truth.
 */

const PRODUCT_CATALOG = {
  'nc':   { name: 'Noir Code',                prices: { '50 ml': 245, '100 ml': 395 } },
  'cr':   { name: 'Cold Reserve',             prices: { '50 ml': 265, '100 ml': 420 } },
  'at':   { name: 'After Trade',              prices: { '50 ml': 235, '100 ml': 375 } },
  'bl':   { name: 'Black Ledger',             prices: { '50 ml': 275, '100 ml': 440 } },
  'vs':   { name: 'Velvet Static',            prices: { '50 ml': 255, '100 ml': 410 } },
  'ic':   { name: 'Initiation Case',          prices: { '5 x 10 ml': 145 } },
  'pis':  { name: 'Private Introduction Set', prices: { '7 x 10 ml': 195 } },
  'nc43': { name: 'Noir Code 00:43',          prices: { '100 ml': 385 } },
  'crb4': { name: 'Cold Reserve Batch 04',    prices: { '100 ml': 345 } },
  'fm':   { name: "Founder's Mark",           prices: { '100 ml': 495 } },
  'nva':  { name: 'Night Vessel Atomizer',    prices: { 'Item': 165 } },
  'sv':   { name: 'Scent Vault',              prices: { 'Item': 285 } },
  'cm':   { name: 'Cold Monolith',            prices: { 'Item': 345 } },
  'cc':   { name: 'Collector Case',           prices: { 'Item': 225 } },
};

const EMAIL_IMAGE_MAP = {
  'Noir Code 00:43':        'EMAIL_IMG_NOIR_CODE_0043',
  'Cold Reserve Batch 04':  'EMAIL_IMG_COLD_RESERVE_BATCH04',
  'Private Introduction':   'EMAIL_IMG_PRIVATE_INTRO',
  "Founder":                'EMAIL_IMG_FOUNDERS_MARK',
  'Noir Code':              'EMAIL_IMG_NOIR_CODE',
  'Cold Reserve':           'EMAIL_IMG_COLD_RESERVE',
  'After Trade':            'EMAIL_IMG_AFTER_TRADE',
  'Black Ledger':           'EMAIL_IMG_BLACK_LEDGER',
  'Velvet Static':          'EMAIL_IMG_VELVET_STATIC',
  'Initiation':             'EMAIL_IMG_INITIATION_CASE',
  'Night Vessel':           'EMAIL_IMG_NIGHT_VESSEL',
  'Scent Vault':            'EMAIL_IMG_SCENT_VAULT',
  'Cold Monolith':          'EMAIL_IMG_COLD_MONOLITH',
  'Collector Case':         'EMAIL_IMG_COLLECTOR_CASE',
};


const PROMO_CODES = {
  'NOIR10': { active: true, type: 'all', discountType: 'percent', discount: 10 },
  'WELCOME15': { active: true, type: 'all', discountType: 'percent', discount: 15 },
  'NOIRCODE50': { active: true, type: 'product', discountType: 'fixed', discount: 50, productIds: ['nc', 'nc43'] },
};

module.exports = { PRODUCT_CATALOG, EMAIL_IMAGE_MAP, PROMO_CODES };
