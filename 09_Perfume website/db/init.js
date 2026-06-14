const Database = require('better-sqlite3');
const path = require('path');
const crypto = require('crypto');
const DB_PATH = path.join(__dirname, 'nmh.db');

function hashPassword(password, salt) {
  if (!salt) salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex');
  return { hash, salt };
}

function verifyPassword(password, hash, salt) {
  const result = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex');
  return result === hash;
}

function initDB() {
  const db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');

  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      password_salt TEXT NOT NULL,
      name TEXT DEFAULT '',
      address TEXT DEFAULT '',
      city TEXT DEFAULT '',
      country TEXT DEFAULT '',
      zip TEXT DEFAULT '',
      lang TEXT DEFAULT 'en',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS orders (
      id TEXT PRIMARY KEY,
      user_id INTEGER,
      status TEXT DEFAULT 'created',
      email TEXT NOT NULL,
      name TEXT NOT NULL,
      address TEXT,
      city TEXT,
      country TEXT,
      zip TEXT,
      lang TEXT DEFAULT 'en',
      items TEXT NOT NULL,
      subtotal REAL NOT NULL,
      shipping REAL DEFAULT 0,
      total REAL NOT NULL,
      currency TEXT,
      network TEXT,
      pay_address TEXT,
      tx_hash TEXT,
      tracking_number TEXT,
      notes TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      paid_at DATETIME,
      shipped_at DATETIME,
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS contacts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      subject TEXT,
      message TEXT NOT NULL,
      telegram TEXT,
      whatsapp TEXT,
      lang TEXT DEFAULT 'en',
      status TEXT DEFAULT 'new',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_orders_email ON orders(email);
    CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);
    CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
  `);

  const upsert = db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)');
  const defaults = {
    'pay_btc': process.env.PAY_BTC || '', 'pay_eth': process.env.PAY_ETH || '',
    'pay_ltc': process.env.PAY_LTC || '', 'pay_trx': process.env.PAY_TRX || '',
    'pay_bnb': process.env.PAY_BNB || '', 'pay_sol': process.env.PAY_SOL || '',
    'pay_usdt_trc20': process.env.PAY_USDT_TRC20 || '', 'pay_usdt_erc20': process.env.PAY_USDT_ERC20 || '',
    'pay_usdt_bep20': process.env.PAY_USDT_BEP20 || '', 'pay_usdt_polygon': process.env.PAY_USDT_POLYGON || '',
    'pay_usdt_solana': process.env.PAY_USDT_SOLANA || '',
    'pay_usdc_erc20': process.env.PAY_USDC_ERC20 || '', 'pay_usdc_polygon': process.env.PAY_USDC_POLYGON || '',
    'pay_usdc_solana': process.env.PAY_USDC_SOLANA || '', 'pay_usdc_base': process.env.PAY_USDC_BASE || '',
    'pay_usdc_arbitrum': process.env.PAY_USDC_ARBITRUM || '',
    'support_instagram': process.env.SUPPORT_INSTAGRAM || '', 'support_telegram': process.env.SUPPORT_TELEGRAM || '',
    'support_whatsapp': process.env.SUPPORT_WHATSAPP || '', 'support_email': process.env.SUPPORT_EMAIL || '',
    'support_x': process.env.SUPPORT_X || '',
    'telegram_bot_token': process.env.TELEGRAM_BOT_TOKEN || '', 'telegram_chat_id': process.env.TELEGRAM_CHAT_ID || '',
    'email_hero_image': process.env.EMAIL_HERO_IMAGE || '',
    'shipping_price': process.env.SHIPPING_PRICE_USD || '25',
    'shipping_free_above': process.env.SHIPPING_FREE_ABOVE || '300',
    'shipping_estimate': process.env.SHIPPING_ESTIMATE_DAYS || '5 to 12',
    'payment_timeout': process.env.PAYMENT_TIMEOUT || '60',
  };
  for (const [k, v] of Object.entries(defaults)) upsert.run(k, v);
  return db;
}

module.exports = { initDB, hashPassword, verifyPassword, DB_PATH };
