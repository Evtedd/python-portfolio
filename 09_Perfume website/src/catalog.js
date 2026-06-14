/*
 * NOIR MAISON HAUTE product catalog and image configuration
 *
 * Edit this file to change prices, sizes, and image URLs.
 * After editing, rebuild: npm run build
 *
 * PRICES: use the "prices" object to set price per size.
 *   Single size products: { "100 ml": 385 }
 *   Multi size products:  { "50 ml": 245, "100 ml": 395 }
 *   No size products:     { "Item": 165 }
 */

export const HERO_IMAGE = "https://i.ibb.co/vvgHmsm2/Chat-GPT-Image-27-2026-17-29-31.png";

export const PRODUCT_IMAGES = {
  noirCode:             { card: "https://i.ibb.co/sdpVKNb3/1.png",                    product: "https://i.ibb.co/7NWtZjJX/2.png",                     gallery: [] },
  coldReserve:          { card: "https://i.ibb.co/Z6QQ0Bb3/Cold-Reserve1.png",         product: "https://i.ibb.co/KpbMVp7r/Cold-Reserve-2.png",         gallery: ["https://i.ibb.co/Zp0ZZLNK/Cold-Reserve-3.png"] },
  afterTrade:           { card: "https://i.ibb.co/jZbfJJRq/After-Trade1.png",          product: "https://i.ibb.co/0RDtJKnW/After-Trade2.png",           gallery: ["https://i.ibb.co/KpgPyW4t/After-Trade3.png"] },
  blackLedger:          { card: "https://i.ibb.co/JwMBmyPF/Black-Ledger1.png",         product: "https://i.ibb.co/0pZBbRR4/Black-Ledger2.png",          gallery: ["https://i.ibb.co/4wPLJkd6/Black-Ledger3.png"] },
  velvetStatic:         { card: "https://i.ibb.co/mwQKvzr/Velvet-Static1.png",         product: "https://i.ibb.co/nMRp3SBY/Velvet-Static2.png",         gallery: [] },
  initiationCase:       { card: "https://i.ibb.co/PG3rzxvw/initiation-Case1.png",      product: "https://i.ibb.co/tptWFFJh/initiation-Case2.png",       gallery: ["https://i.ibb.co/VYz6gxGF/sealed-archive-perfume-sample.png"] },
  privateIntro:         { card: "https://i.ibb.co/r2MchnG0/private-Intro1.png",         product: "https://i.ibb.co/MDXMZccK/private-Intro2.png",         gallery: [] },
  noirCode0043:         { card: "https://i.ibb.co/fz0S0Sbb/Noir-Code-0043-1.png",      product: "https://i.ibb.co/DDqSJCHT/Noir-Code-0043-2.png",       gallery: [] },
  coldReserveBatch04:   { card: "https://i.ibb.co/gL2j0KbR/Batch-04-1.png",            product: "https://i.ibb.co/KxTjyqNr/Batch-04-2.png",             gallery: [] },
  foundersMarkEdition:  { card: "https://i.ibb.co/7xywJV1b/After-Trade-Batch-01-1.png", product: "https://i.ibb.co/CpcgdFhr/After-Trade-Batch-01-2.png", gallery: [] },
  nightVessel:          { card: "https://i.ibb.co/BXqLrVp/Night-Vessel-1.png",          product: "https://i.ibb.co/BXqLrVp/Night-Vessel-1.png",          gallery: [] },
  scentVault:           { card: "https://i.ibb.co/TBW882g2/Scent-Vault-1.png",          product: "https://i.ibb.co/67bcQxzH/Scent-Vault-2.png",          gallery: [] },
  coldMonolith:         { card: "https://i.ibb.co/mV0vfGfm/stone-aromatic1.png",        product: "https://i.ibb.co/yng6xnH0/stone-aromatic2.png",        gallery: [] },
  collectorCase:        { card: "https://i.ibb.co/4w8c1r00/collector-case1.png",         product: "https://i.ibb.co/8DhCng3P/collector-case2.png",        gallery: [] },
};

// PRODUCT PRICES by size, in USD
// To change a price: edit the number next to the size.
// To add a size: add a new "size": price entry.
export const PRODUCT_PRICES = {
  nc:   { name: "Noir Code",                  prices: { "50 ml": 245, "100 ml": 395 } },
  cr:   { name: "Cold Reserve",               prices: { "50 ml": 265, "100 ml": 420 } },
  at:   { name: "After Trade",                prices: { "50 ml": 235, "100 ml": 375 } },
  bl:   { name: "Black Ledger",               prices: { "50 ml": 275, "100 ml": 440 } },
  vs:   { name: "Velvet Static",              prices: { "50 ml": 255, "100 ml": 410 } },
  ic:   { name: "Initiation Case",            prices: { "5 x 10 ml": 145 } },
  pis:  { name: "Private Introduction Set",   prices: { "7 x 10 ml": 195 } },
  nc43: { name: "Noir Code 00:43",            prices: { "100 ml": 385 } },
  crb4: { name: "Cold Reserve Batch 04",      prices: { "100 ml": 345 } },
  fm:   { name: "Founder's Mark",             prices: { "100 ml": 495 } },
  nva:  { name: "Night Vessel Atomizer",      prices: { "Item": 165 } },
  sv:   { name: "Scent Vault",                prices: { "Item": 285 } },
  cm:   { name: "Cold Monolith",              prices: { "Item": 345 } },
  cc:   { name: "Collector Case",             prices: { "Item": 225 } },
};

// Helper: get price for a product by size
export function getPrice(productId, size) {
  const prod = PRODUCT_PRICES[productId];
  if (!prod) return 0;
  if (prod.prices[size] !== undefined) return prod.prices[size];
  // Fallback: return first price
  const vals = Object.values(prod.prices);
  return vals[0] || 0;
}

// Helper: get starting (lowest) price for display
export function getStartPrice(productId) {
  const prod = PRODUCT_PRICES[productId];
  if (!prod) return 0;
  return Math.min(...Object.values(prod.prices));
}

// PROMO CODES
// type: 'all' = entire cart, 'product' = specific products only
// discountType: 'percent' or 'fixed' (USD)
// productIds: only for type='product', array of product IDs from PRODUCT_PRICES
// active: set to false to disable without deleting
export const PROMO_CODES = {
  'NOIR10': {
    active: true,
    type: 'all',
    discountType: 'percent',
    discount: 10,
    description: { en: '10% off entire order', ru: 'Скидка 10% на весь заказ', es: '10% en todo el pedido' }
  },
  'WELCOME15': {
    active: true,
    type: 'all',
    discountType: 'percent',
    discount: 15,
    description: { en: '15% welcome discount', ru: 'Приветственная скидка 15%', es: '15% de bienvenida' }
  },
  'NOIRCODE50': {
    active: true,
    type: 'product',
    discountType: 'fixed',
    discount: 50,
    productIds: ['nc', 'nc43'],
    description: { en: '$50 off Noir Code', ru: 'Скидка $50 на Noir Code', es: '$50 en Noir Code' }
  },
};
