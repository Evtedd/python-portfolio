require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const path = require('path');
const fs = require('fs');
const https = require('https');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const QRCode = require('qrcode');
const nodemailer = require('nodemailer');
const { initDB, hashPassword, verifyPassword } = require('./db/init');

const app = express();
const PORT = process.env.PORT || 3000;
const db = initDB();

if (!process.env.SESSION_SECRET || process.env.SESSION_SECRET === 'change-this-to-a-random-string' || process.env.SESSION_SECRET === 'replace-with-long-random-string') {
  console.warn('\n  ⚠ SESSION_SECRET is not set or still default!');
  console.warn('  ⚠ Generate one: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"');
  console.warn('  ⚠ Using temporary random secret for this session.\n');
  process.env.SESSION_SECRET = crypto.randomBytes(32).toString('hex');
}
const SESSION_SECRET = process.env.SESSION_SECRET;

const distDir = path.join(__dirname, 'dist');
const distExists = fs.existsSync(path.join(distDir, 'index.html'));
if (!distExists) console.warn('\n  ⚠ dist/ not found. Run "npm run build".\n');

app.use(compression());
app.use(helmet({ contentSecurityPolicy: false, crossOriginEmbedderPolicy: false }));
app.use(cors());
app.use(express.json({ limit: '1mb' }));
if (distExists) app.use(express.static(distDir, { maxAge: '30d', immutable: true, index: false }));

const apiLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 });
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 20 });
const contactLimiter = rateLimit({ windowMs: 60 * 60 * 1000, max: 10 });

const { PRODUCT_CATALOG, EMAIL_IMAGE_MAP, PROMO_CODES } = require('./catalog.server.js');

const ENV_SETTINGS = {
  pay_btc: process.env.PAY_BTC || '',
  pay_eth: process.env.PAY_ETH || '',
  pay_ltc: process.env.PAY_LTC || '',
  pay_trx: process.env.PAY_TRX || '',
  pay_bnb: process.env.PAY_BNB || '',
  pay_sol: process.env.PAY_SOL || '',
  pay_usdt_trc20: process.env.PAY_USDT_TRC20 || '',
  pay_usdt_erc20: process.env.PAY_USDT_ERC20 || '',
  pay_usdt_bep20: process.env.PAY_USDT_BEP20 || '',
  pay_usdt_polygon: process.env.PAY_USDT_POLYGON || '',
  pay_usdt_solana: process.env.PAY_USDT_SOLANA || '',
  pay_usdc_erc20: process.env.PAY_USDC_ERC20 || '',
  pay_usdc_polygon: process.env.PAY_USDC_POLYGON || '',
  pay_usdc_solana: process.env.PAY_USDC_SOLANA || '',
  pay_usdc_base: process.env.PAY_USDC_BASE || '',
  pay_usdc_arbitrum: process.env.PAY_USDC_ARBITRUM || '',
  support_instagram: process.env.SUPPORT_INSTAGRAM || '',
  support_telegram: process.env.SUPPORT_TELEGRAM || '',
  support_whatsapp: process.env.SUPPORT_WHATSAPP || '',
  support_email: process.env.SUPPORT_EMAIL || '',
  support_x: process.env.SUPPORT_X || '',
  telegram_bot_token: process.env.TELEGRAM_BOT_TOKEN || '',
  telegram_chat_id: process.env.TELEGRAM_CHAT_ID || '',
  email_hero_image: process.env.EMAIL_HERO_IMAGE || '',
  shipping_price: process.env.SHIPPING_PRICE_USD || '25',
  shipping_free_above: process.env.SHIPPING_FREE_ABOVE || '300',
  shipping_estimate: process.env.SHIPPING_ESTIMATE_DAYS || '5 to 12',
  payment_timeout: process.env.PAYMENT_TIMEOUT || '60',
};

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function cleanOneLine(value, max = 120) {
  return String(value || '').replace(/\s+/g, ' ').trim().slice(0, max);
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i.test(String(email || '').trim());
}

function buildShortEmailError(error) {
  return String(error || 'unknown error').replace(/\s+/g, ' ').trim().slice(0, 180);
}

function getSetting(key) {
  const envValue = String(ENV_SETTINGS[key] || '').trim();
  if (envValue) return envValue;
  const row = db.prepare('SELECT value FROM settings WHERE key = ?').get(key);
  return row ? String(row.value || '').trim() : '';
}

function getAllSettings() {
  const out = {};
  const rows = db.prepare('SELECT key, value FROM settings').all();
  for (const row of rows) {
    const v = String(row.value || '').trim();
    if (v) out[row.key] = v;
  }
  for (const [key, value] of Object.entries(ENV_SETTINGS)) {
    const v = String(value || '').trim();
    if (v) out[key] = v;
  }
  return out;
}

function getPaymentConfig() {
  const s = getAllSettings();
  const config = [];

  [
    ['BTC', 'Bitcoin', 'pay_btc'],
    ['ETH', 'Ethereum', 'pay_eth'],
    ['LTC', 'Litecoin', 'pay_ltc'],
    ['TRX', 'TRON', 'pay_trx'],
    ['BNB', 'BNB', 'pay_bnb'],
    ['SOL', 'Solana', 'pay_sol']
  ].forEach(([code, name, key]) => {
    if (String(s[key] || '').trim()) config.push({ code, name, networks: null, address: s[key] });
  });

  const mkNets = (prefix, pairs) => {
    const nets = [];
    for (const [id, name, suffix] of pairs) {
      const address = String(s[prefix + suffix] || '').trim();
      if (address) nets.push({ id, name, address });
    }
    return nets;
  };

  const usdtNets = mkNets('pay_usdt_', [
    ['TRC20', 'Tron (TRC20)', 'trc20'],
    ['ERC20', 'Ethereum (ERC20)', 'erc20'],
    ['BEP20', 'BSC (BEP20)', 'bep20'],
    ['POLYGON', 'Polygon', 'polygon'],
    ['SOLANA', 'Solana', 'solana']
  ]);
  if (usdtNets.length) config.push({ code: 'USDT', name: 'Tether (USDT)', networks: usdtNets });

  const usdcNets = mkNets('pay_usdc_', [
    ['ERC20', 'Ethereum (ERC20)', 'erc20'],
    ['POLYGON', 'Polygon', 'polygon'],
    ['SOLANA', 'Solana', 'solana'],
    ['BASE', 'Base', 'base'],
    ['ARBITRUM', 'Arbitrum', 'arbitrum']
  ]);
  if (usdcNets.length) config.push({ code: 'USDC', name: 'USD Coin (USDC)', networks: usdcNets });

  return config;
}

function getSupportLinks() {
  const s = getAllSettings();
  return {
    instagram: s.support_instagram || '',
    telegram: s.support_telegram || '',
    whatsapp: s.support_whatsapp || '',
    email: s.support_email || ''
  };
}

function getShippingConfig() {
  return {
    price: parseFloat(getSetting('shipping_price') || '25'),
    freeAbove: parseFloat(getSetting('shipping_free_above') || '300'),
    estimate: getSetting('shipping_estimate') || '5 to 12'
  };
}

function validateOrderItems(items) {
  let subtotal = 0;
  const validated = [];

  for (const item of items || []) {
    const product = PRODUCT_CATALOG[item.id];
    if (!product) return { error: `Unknown product: ${item.id}` };
    const qty = Math.max(1, parseInt(item.qty, 10) || 1);
    const size = cleanOneLine(item.size, 20);
    // Look up price by size; fallback to first available price
    let price = product.prices[size];
    if (price === undefined) {
      const vals = Object.values(product.prices);
      price = vals[0] || 0;
    }
    subtotal += price * qty;
    validated.push({
      id: item.id,
      name: product.name + (item.code ? ` ${cleanOneLine(item.code, 40)}` : ''),
      size,
      qty,
      price
    });
  }

  return { items: validated, subtotal };
}

function validateOrderInput(body = {}) {
  const email = cleanOneLine(body.email, 120).toLowerCase();
  const name = cleanOneLine(body.name, 80);
  const address = cleanOneLine(body.address, 140);
  const city = cleanOneLine(body.city, 80);
  const country = cleanOneLine(body.country, 56);
  const zip = cleanOneLine(body.zip, 20);
  const lang = ['en', 'ru', 'es'].includes(body.lang) ? body.lang : 'en';

  if (!isValidEmail(email)) return { error: 'Invalid email address' };
  if (name.length < 2) return { error: 'Invalid name' };
  if (address.length < 4) return { error: 'Invalid address' };
  if (!/^[A-Za-zÀ-ÿА-Яа-яЁё0-9\s.'-]{2,80}$/.test(city)) return { error: 'Invalid city' };
  if (!/^[A-Za-zÀ-ÿА-Яа-яЁё\s.'-]{2,56}$/.test(country)) return { error: 'Invalid country' };
  if (!/^[A-Za-z0-9\s-]{2,20}$/.test(zip)) return { error: 'Invalid postal code' };
  if (!Array.isArray(body.items) || body.items.length === 0) return { error: 'Cart is empty' };

  return { email, name, address, city, country, zip, lang, items: body.items };
}

const EMAIL_MODE = String(process.env.EMAIL_MODE || (process.env.RESEND_API_KEY ? 'resend_api' : 'smtp')).trim().toLowerCase();
const RESEND_API_KEY = String(process.env.RESEND_API_KEY || '').trim();
let transporter = null;
if (EMAIL_MODE === 'smtp' && process.env.SMTP_HOST) {
  transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT || '587', 10),
    secure: String(process.env.SMTP_SECURE || '').toLowerCase() === 'true',
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
  });
}

function httpsRequestJSON({ hostname, path: requestPath, method = 'GET', headers = {}, body = null, timeout = 15000 }) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = https.request({
      hostname,
      path: requestPath,
      method,
      timeout,
      headers: {
        ...(data ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {}),
        ...headers
      }
    }, (res) => {
      let raw = '';
      res.on('data', d => raw += d);
      res.on('end', () => {
        let parsed = {};
        try { parsed = raw ? JSON.parse(raw) : {}; } catch {}
        if (res.statusCode >= 200 && res.statusCode < 300) return resolve({ statusCode: res.statusCode, data: parsed, raw });
        const message = parsed.message || parsed.error || raw || `HTTP ${res.statusCode}`;
        reject(new Error(message));
      });
    });
    req.on('timeout', () => req.destroy(new Error('HTTPS request timeout')));
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function verifyEmailTransport() {
  if (EMAIL_MODE === 'resend_api') {
    if (!RESEND_API_KEY) {
      console.warn('[EMAIL] Resend API mode selected, but RESEND_API_KEY is empty');
      return false;
    }
    console.log('[EMAIL] Mode: resend_api');
    return true;
  }

  if (!transporter) {
    console.warn('[EMAIL] SMTP transporter is not configured');
    return false;
  }

  try {
    await transporter.verify();
    console.log('[EMAIL] SMTP verified successfully');
    return true;
  } catch (e) {
    console.error('[EMAIL] SMTP verify failed:', buildShortEmailError(e.message));
    return false;
  }
}

async function sendEmail(to, subject, html, context = {}) {
  const safeTo = cleanOneLine(to, 140);
  if (!isValidEmail(safeTo)) {
    const error = 'invalid recipient email';
    console.error('[EMAIL] Send blocked:', JSON.stringify({ to: safeTo, subject, context, error }, null, 2));
    return { ok: false, error };
  }

  const from = process.env.EMAIL_FROM || 'Noir Maison Haute <orders@noirmaisonhaute.art>';
  console.log(`[EMAIL] Sending → to=${safeTo} mode=${EMAIL_MODE} subject="${subject}"`);

  try {
    if (EMAIL_MODE === 'resend_api') {
      if (!RESEND_API_KEY) throw new Error('RESEND_API_KEY is missing');
      const response = await httpsRequestJSON({
        hostname: 'api.resend.com',
        path: '/emails',
        method: 'POST',
        headers: { Authorization: `Bearer ${RESEND_API_KEY}` },
        body: { from, to: [safeTo], subject, html }
      });
      console.log('[EMAIL] Resend API sent OK:', JSON.stringify({ to: safeTo, id: response.data?.id || '' }));
      return { ok: true, id: response.data?.id || '' };
    }

    if (!transporter) throw new Error('SMTP transporter is not configured');
    const info = await transporter.sendMail({ from, to: safeTo, subject, html });
    console.log('[EMAIL] SMTP sent OK:', JSON.stringify({ to: safeTo, id: info.messageId || '' }));
    return { ok: true, id: info.messageId || '' };
  } catch (e) {
    const error = e.message || 'unknown email error';
    console.error('[EMAIL] Send failed:', JSON.stringify({ to: safeTo, subject, context, error }, null, 2));
    return { ok: false, error };
  }
}

const TG = {
  reviewTitle: 'NMH: оплата отправлена',
  awaitingTitle: 'NMH: заказ создан',
  confirmedTitle: 'NMH: оплата подтверждена',
  shippedTitle: 'NMH: заказ отправлен',
  contactTitle: 'NMH: новое сообщение',
  buttonConfirm: 'Подтвердить оплату',
  callbackProcessing: 'Подтверждаю...',
  callbackDone: 'Оплата подтверждена',
  callbackAlready: 'Уже обработано',
  callbackNeedPaid: 'Сначала клиент должен отметить оплату',
  callbackNotFound: 'Заказ не найден',
  emailSent: 'Письмо отправлено',
  emailFailed: 'Письмо не отправлено',
};

function getTelegramToken() {
  return getSetting('telegram_bot_token') || process.env.TELEGRAM_BOT_TOKEN || '';
}

function getTelegramChatId() {
  return getSetting('telegram_chat_id') || process.env.TELEGRAM_CHAT_ID || '';
}

function getTelegramWebhookUrl() {
  return String(process.env.TELEGRAM_WEBHOOK_URL || '').trim();
}

function getTelegramMode() {
  const mode = String(process.env.TELEGRAM_MODE || 'polling').trim().toLowerCase();
  if (mode === 'webhook' && getTelegramWebhookUrl()) return 'webhook';
  return 'polling';
}

function telegramAPI(token, method, payload = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload);
    const req = https.request({
      hostname: 'api.telegram.org',
      path: `/bot${token}/${method}`,
      method: 'POST',
      timeout: 35000,
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    }, (res) => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => {
        let parsed = {};
        try { parsed = body ? JSON.parse(body) : {}; } catch {}
        if (res.statusCode >= 200 && res.statusCode < 300 && parsed.ok !== false) {
          console.log(`[TG] ${method} OK`);
          resolve(parsed);
        } else {
          const message = parsed.description || body || `Telegram ${method} failed`;
          console.error(`[TG ${method}]`, message);
          reject(new Error(message));
        }
      });
    });
    req.on('timeout', () => req.destroy(new Error(`Telegram ${method} timeout`)));
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function sendTelegram(text, replyMarkup = null) {
  const token = getTelegramToken();
  const chatId = getTelegramChatId();
  if (!token || !chatId) return Promise.resolve(null);
  const payload = { chat_id: chatId, text, parse_mode: 'HTML', disable_web_page_preview: true };
  if (replyMarkup) payload.reply_markup = replyMarkup;
  return telegramAPI(token, 'sendMessage', payload).catch(err => {
    console.error('[TG sendMessage]', err.message);
    return null;
  });
}

function answerCallbackQuery(token, callbackQueryId, text) {
  if (!token || !callbackQueryId) return Promise.resolve(null);
  return telegramAPI(token, 'answerCallbackQuery', {
    callback_query_id: callbackQueryId,
    text: text || 'OK',
    show_alert: false,
    cache_time: 0
  }).catch(err => {
    console.error('[TG answerCallbackQuery]', err.message);
    return null;
  });
}

function editTelegramReplyMarkup(chatId, messageId, replyMarkup = { inline_keyboard: [] }) {
  const token = getTelegramToken();
  if (!token || !chatId || !messageId) return Promise.resolve(null);
  return telegramAPI(token, 'editMessageReplyMarkup', {
    chat_id: chatId,
    message_id: messageId,
    reply_markup: replyMarkup
  }).catch(err => {
    console.error('[TG editMessageReplyMarkup]', err.message);
    return null;
  });
}

function tgAddress(order) {
  return [cleanOneLine(order.address, 120), cleanOneLine(order.city, 80), cleanOneLine(order.country, 56), cleanOneLine(order.zip, 20)]
    .filter(Boolean)
    .join(', ');
}

function tgItems(items) {
  return (items || []).map(item => `• ${escapeHtml(item.name)} ×${item.qty}: $${item.price * item.qty}`).join('\n');
}

function buildTelegramOrderMessage(order, items, mode = 'review') {
  const title = mode === 'awaiting_payment' ? TG.awaitingTitle : mode === 'confirmed' ? TG.confirmedTitle : mode === 'shipped' ? TG.shippedTitle : TG.reviewTitle;
  const address = tgAddress(order);
  const networkLine = order.network ? `\nСеть: <code>${escapeHtml(order.network)}</code>` : '';
  const emailLine = order.email ? `\nEmail: <code>${escapeHtml(order.email)}</code>` : '';
  const addressLine = address ? `\nАдрес: ${escapeHtml(address)}` : '';
  const trackingLine = order.tracking_number ? `\nТрек: <code>${escapeHtml(order.tracking_number)}</code>` : '';
  return `<b>${title}</b>\n\n<blockquote>Заказ: <code>${escapeHtml(order.id)}</code>\nСумма: <b>$${order.total}</b>\nОплата: <code>${escapeHtml(order.currency || 'нет')}</code>${networkLine}\nСтатус: <b>${mode === 'awaiting_payment' ? 'Ожидает оплату' : mode === 'confirmed' ? 'Подтверждён' : mode === 'shipped' ? 'Отправлен' : 'Нужна проверка'}</b></blockquote>\n\n<blockquote>Клиент: ${escapeHtml(order.name || 'нет')}${emailLine}${addressLine}</blockquote>\n\n<blockquote>Товары:\n${tgItems(items)}</blockquote>${trackingLine ? `\n\n<blockquote>${trackingLine.trim()}</blockquote>` : ''}`;
}

function buildTelegramEmailResultLine(emailResult, email) {
  if (emailResult.ok) return `${TG.emailSent}: <code>${escapeHtml(email)}</code>`;
  return `${TG.emailFailed}: <code>${escapeHtml(buildShortEmailError(emailResult.error))}</code>`;
}

async function processTelegramUpdate(update) {
  if (!update || !update.callback_query) return;

  const cbq = update.callback_query;
  const cbData = cbq.data || '';
  const token = getTelegramToken();
  if (!token) return;

  if (!cbData.startsWith('confirm_')) {
    await answerCallbackQuery(token, cbq.id, 'Неизвестное действие');
    return;
  }

  const orderId = cbData.replace('confirm_', '');
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
  if (!order) {
    await answerCallbackQuery(token, cbq.id, TG.callbackNotFound);
    return;
  }

  if (order.status === 'confirmed' || order.status === 'paid' || order.status === 'shipped') {
    await answerCallbackQuery(token, cbq.id, TG.callbackAlready);
    return;
  }

  if (order.status !== 'awaiting_confirmation') {
    await answerCallbackQuery(token, cbq.id, TG.callbackNeedPaid);
    return;
  }

  await answerCallbackQuery(token, cbq.id, TG.callbackProcessing);

  db.prepare('UPDATE orders SET status = ?, paid_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run('confirmed', orderId);
  const updatedOrder = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId) || order;
  const items = JSON.parse(updatedOrder.items || '[]');
  const emailResult = await sendEmail(updatedOrder.email, getEmailSubject(updatedOrder.lang, updatedOrder.id), buildConfirmEmail(updatedOrder, items), { source: 'telegram_callback', orderId });
  const tgMessage = `${buildTelegramOrderMessage(updatedOrder, items, 'confirmed')}\n\n<blockquote>${buildTelegramEmailResultLine(emailResult, updatedOrder.email)}</blockquote>`;

  await sendTelegram(tgMessage);
  if (cbq.message?.chat?.id && cbq.message?.message_id) {
    await editTelegramReplyMarkup(cbq.message.chat.id, cbq.message.message_id, { inline_keyboard: [] });
  }
}

app.post('/api/telegram/webhook', (req, res) => {
  res.json({ ok: true });
  processTelegramUpdate(req.body).catch(err => console.error('[TG webhook]', err.message));
});

let tgPollingStarted = false;
let tgOffset = 0;

async function startTelegramLongPolling() {
  if (tgPollingStarted) return;
  const token = getTelegramToken();
  if (!token) return;
  tgPollingStarted = true;

  try {
    await telegramAPI(token, 'deleteWebhook', { drop_pending_updates: false });
  } catch (e) {
    console.error('[TG deleteWebhook]', e.message);
  }

  console.log('[TG] Polling enabled');
  while (true) {
    try {
      const response = await telegramAPI(token, 'getUpdates', {
        offset: tgOffset,
        timeout: 25,
        allowed_updates: ['callback_query']
      });
      const updates = Array.isArray(response.result) ? response.result : [];
      for (const update of updates) {
        tgOffset = Math.max(tgOffset, (update.update_id || 0) + 1);
        await processTelegramUpdate(update);
      }
    } catch (e) {
      console.error('[TG polling]', e.message);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}

async function bootstrapTelegram() {
  const token = getTelegramToken();
  if (!token) {
    console.warn('[TG] Bot token is empty');
    return;
  }

  if (getTelegramMode() === 'webhook') {
    const webhookUrl = getTelegramWebhookUrl();
    try {
      await telegramAPI(token, 'setWebhook', { url: webhookUrl });
      console.log('[TG] Webhook enabled:', webhookUrl);
      return;
    } catch (e) {
      console.error('[TG setWebhook]', e.message);
      console.log('[TG] Falling back to polling');
    }
  }

  startTelegramLongPolling().catch(err => console.error('[TG polling fatal]', err.message));
}

function buildCryptoQR(currency, network, address, amount) {
  switch (currency) {
    case 'BTC': return `bitcoin:${address}?amount=${amount}`;
    case 'ETH': return `ethereum:${address}?value=${amount}`;
    case 'LTC': return `litecoin:${address}?amount=${amount}`;
    case 'TRX': return `tron:${address}`;
    case 'BNB': return `ethereum:${address}?value=${amount}`;
    case 'SOL': return `solana:${address}?amount=${amount}`;
    case 'USDT':
    case 'USDC':
      if (network === 'TRC20') return `tron:${address}`;
      if (network === 'SOLANA') return `solana:${address}?amount=${amount}`;
      if (['ERC20', 'BEP20', 'POLYGON', 'BASE', 'ARBITRUM'].includes(network)) return `ethereum:${address}`;
      return address;
    default:
      return address;
  }
}

function generateToken(userId) {
  const payload = `${userId}:${Date.now()}:${crypto.randomBytes(16).toString('hex')}`;
  const hmac = crypto.createHmac('sha256', SESSION_SECRET).update(payload).digest('hex');
  return Buffer.from(`${payload}:${hmac}`).toString('base64');
}

function verifyToken(token) {
  try {
    const decoded = Buffer.from(token, 'base64').toString();
    const parts = decoded.split(':');
    const hmac = parts.pop();
    const payload = parts.join(':');
    const expected = crypto.createHmac('sha256', SESSION_SECRET).update(payload).digest('hex');
    if (hmac !== expected) return null;
    const userId = parseInt(parts[0], 10);
    const ts = parseInt(parts[1], 10);
    if (Date.now() - ts > 30 * 24 * 60 * 60 * 1000) return null;
    return userId;
  } catch {
    return null;
  }
}

function userAuth(req, res, next) {
  const token = req.headers['x-auth-token'];
  if (!token) return res.status(401).json({ error: 'Not authenticated' });
  const userId = verifyToken(token);
  if (!userId) return res.status(401).json({ error: 'Invalid or expired token' });
  req.userId = userId;
  next();
}

app.post('/api/auth/register', authLimiter, (req, res) => {
  const { email, password, name, lang } = req.body;
  if (!email || !password || password.length < 6) return res.status(400).json({ error: 'Email and password (min 6 chars) required' });
  const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(String(email).toLowerCase());
  if (existing) return res.status(409).json({ error: 'Email already registered' });
  const { hash, salt } = hashPassword(password);
  const result = db.prepare('INSERT INTO users(email, password_hash, password_salt, name, lang) VALUES(?,?,?,?,?)').run(String(email).toLowerCase(), hash, salt, name || '', lang || 'en');
  const token = generateToken(result.lastInsertRowid);
  res.json({ token, user: { id: result.lastInsertRowid, email: String(email).toLowerCase(), name: name || '', lang: lang || 'en' } });
});

app.post('/api/auth/login', authLimiter, (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(String(email).toLowerCase());
  if (!user || !verifyPassword(password, user.password_hash, user.password_salt)) return res.status(401).json({ error: 'Invalid email or password' });
  const token = generateToken(user.id);
  res.json({ token, user: { id: user.id, email: user.email, name: user.name, address: user.address, city: user.city, country: user.country, zip: user.zip, lang: user.lang } });
});

app.get('/api/auth/me', userAuth, (req, res) => {
  const user = db.prepare('SELECT id, email, name, address, city, country, zip, lang FROM users WHERE id = ?').get(req.userId);
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});

app.patch('/api/auth/me', userAuth, (req, res) => {
  const { name, address, city, country, zip, lang } = req.body;
  const updates = [];
  const values = [];
  if (name !== undefined) { updates.push('name=?'); values.push(name); }
  if (address !== undefined) { updates.push('address=?'); values.push(address); }
  if (city !== undefined) { updates.push('city=?'); values.push(city); }
  if (country !== undefined) { updates.push('country=?'); values.push(country); }
  if (zip !== undefined) { updates.push('zip=?'); values.push(zip); }
  if (lang !== undefined) { updates.push('lang=?'); values.push(lang); }
  if (updates.length) {
    values.push(req.userId);
    db.prepare(`UPDATE users SET ${updates.join(',')} WHERE id=?`).run(...values);
  }
  res.json({ ok: true });
});

app.get('/api/auth/orders', userAuth, (req, res) => {
  const orders = db.prepare('SELECT id, status, total, currency, created_at, paid_at, shipped_at, tracking_number FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 50').all(req.userId);
  res.json(orders);
});

// ANALYTICS BOT (separate from order bot)
const ANALYTICS_BOT_TOKEN = process.env.ANALYTICS_BOT_TOKEN || '';
const ANALYTICS_CHAT_ID = process.env.ANALYTICS_CHAT_ID || '';

function sendAnalytics(text) {
  if (!ANALYTICS_BOT_TOKEN || !ANALYTICS_CHAT_ID) return;
  const payload = { chat_id: ANALYTICS_CHAT_ID, text, parse_mode: 'HTML', disable_web_page_preview: true };
  const data = JSON.stringify(payload);
  const req = https.request({ hostname: 'api.telegram.org', path: `/bot${ANALYTICS_BOT_TOKEN}/sendMessage`, method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } },
    res => { let b = ''; res.on('data', d => b += d); res.on('end', () => {}); });
  req.on('error', () => {});
  req.write(data); req.end();
}

// Track site visits
let visitCount = 0;
const productViews = {};

app.post('/api/analytics/visit', (req, res) => {
  visitCount++;
  const { page, product, lang, ua } = req.body || {};
  if (product) productViews[product] = (productViews[product] || 0) + 1;
  const time = new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' });
  sendAnalytics(`👁 <b>Visit #${visitCount}</b>\n${time}\n📄 ${page || 'home'}${product ? '\n🧴 ' + product : ''}\n🌐 ${lang || 'en'}\n📱 ${(ua || '').slice(0, 60)}`);
  res.json({ ok: true });
});

app.get('/api/analytics/stats', (req, res) => {
  const totalOrders = db.prepare('SELECT COUNT(*) as c FROM orders').get().c;
  const confirmedOrders = db.prepare("SELECT COUNT(*) as c FROM orders WHERE status='confirmed'").get().c;
  const revenue = db.prepare("SELECT COALESCE(SUM(total),0) as s FROM orders WHERE status='confirmed'").get().s;
  res.json({ visits: visitCount, totalOrders, confirmedOrders, revenue, topProducts: productViews });
});

// PROMO CODE VALIDATION
app.post('/api/promo/validate', apiLimiter, (req, res) => {
  const { code, items } = req.body;
  if (!code) return res.status(400).json({ error: 'No code provided' });
  const promo = PROMO_CODES[code.toUpperCase()];
  if (!promo || !promo.active) return res.status(400).json({ error: 'invalid' });

  let discount = 0;
  const validatedItems = (items || []).map(item => {
    const prod = PRODUCT_CATALOG[item.id];
    if (!prod) return item;
    const size = item.size || Object.keys(prod.prices)[0];
    const price = prod.prices[size] || Object.values(prod.prices)[0] || 0;
    const qty = item.qty || 1;
    let itemDiscount = 0;
    if (promo.type === 'all' || (promo.type === 'product' && promo.productIds && promo.productIds.includes(item.id))) {
      if (promo.discountType === 'percent') itemDiscount = Math.round(price * qty * promo.discount / 100);
      else itemDiscount = Math.min(promo.discount * qty, price * qty);
    }
    discount += itemDiscount;
    return { ...item, discount: itemDiscount };
  });

  if (discount <= 0) return res.status(400).json({ error: 'not_applicable' });
  res.json({ valid: true, code: code.toUpperCase(), discount, discountType: promo.discountType, discountValue: promo.discount, type: promo.type });
});

app.get('/api/config', (req, res) => {
  res.json({
    currencies: getPaymentConfig().map(currency => ({
      code: currency.code,
      name: currency.name,
      networks: currency.networks ? currency.networks.map(network => ({ id: network.id, name: network.name })) : null
    })),
    support: getSupportLinks(),
    shipping: getShippingConfig(),
    paymentTimeout: parseInt(getSetting('payment_timeout') || '60', 10),
    catalog: Object.entries(PRODUCT_CATALOG).map(([id, p]) => ({ id, name: p.name, prices: p.prices }))
  });
});

app.post('/api/orders', apiLimiter, (req, res) => {
  const orderInput = validateOrderInput(req.body);
  if (orderInput.error) return res.status(400).json({ error: orderInput.error });

  const validation = validateOrderItems(orderInput.items);
  if (validation.error) return res.status(400).json({ error: validation.error });

  const shipping = getShippingConfig();
  const shippingCost = validation.subtotal >= shipping.freeAbove ? 0 : shipping.price;

  // Apply promo code if provided
  let promoDiscount = 0;
  let promoCode = '';
  const rawPromo = (req.body.promoCode || '').toUpperCase().trim();
  if (rawPromo && PROMO_CODES[rawPromo] && PROMO_CODES[rawPromo].active) {
    const promo = PROMO_CODES[rawPromo];
    for (const item of validation.items) {
      if (promo.type === 'all' || (promo.type === 'product' && promo.productIds && promo.productIds.includes(item.id))) {
        if (promo.discountType === 'percent') promoDiscount += Math.round(item.price * item.qty * promo.discount / 100);
        else promoDiscount += Math.min(promo.discount * item.qty, item.price * item.qty);
      }
    }
    if (promoDiscount > 0) promoCode = rawPromo;
  }

  const total = Math.max(0, validation.subtotal + shippingCost - promoDiscount);

  let userId = null;
  const authToken = req.headers['x-auth-token'];
  if (authToken) { const uid = verifyToken(authToken); if (uid) userId = uid; }

  const id = 'NMH' + uuidv4().slice(0, 8).toUpperCase();
  const notes = promoCode ? `Promo: ${promoCode}, discount $${promoDiscount}` : '';
  db.prepare(`INSERT INTO orders(id, user_id, email, name, address, city, country, zip, lang, items, subtotal, shipping, total, status, notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'created',?)`)
    .run(id, userId, orderInput.email, orderInput.name, orderInput.address, orderInput.city, orderInput.country, orderInput.zip, orderInput.lang, JSON.stringify(validation.items), validation.subtotal, shippingCost, total, notes);

  // Analytics
  sendAnalytics(`🛒 <b>Order Created</b>\n${id}\n$${total}${promoCode ? `\n🏷 Promo: ${promoCode}, discount $${promoDiscount}` : ''}`);

  res.json({ orderId: id, subtotal: validation.subtotal, shipping: shippingCost, discount: promoDiscount, promoCode, total });
});

app.post('/api/orders/:id/pay', apiLimiter, async (req, res) => {
  const { currency, network } = req.body;
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'Not found' });

  const config = getPaymentConfig();
  const currentCurrency = config.find(entry => entry.code === currency);
  if (!currentCurrency) return res.status(400).json({ error: 'Currency not available' });

  let payAddress = '';
  let netId = network || null;
  if (currentCurrency.networks) {
    if (!network) return res.status(400).json({ error: 'Network required' });
    const net = currentCurrency.networks.find(entry => entry.id === network);
    if (!net) return res.status(400).json({ error: 'Network not available' });
    payAddress = net.address;
  } else {
    payAddress = currentCurrency.address;
  }

  db.prepare('UPDATE orders SET currency=?, network=?, pay_address=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?').run(currency, netId, payAddress, 'awaiting_payment', req.params.id);
  const updatedOrder = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id) || { ...order, currency, network: netId, pay_address: payAddress, status: 'awaiting_payment' };

  const qrContent = buildCryptoQR(currency, netId, payAddress, updatedOrder.total);
  const qr = await QRCode.toDataURL(qrContent, { width: 280, margin: 2, color: { dark: '#c9a96e', light: '#0a0a0a' } });

  const items = JSON.parse(updatedOrder.items || '[]');
  await sendTelegram(buildTelegramOrderMessage(updatedOrder, items, 'awaiting_payment'));

  res.json({
    orderId: req.params.id,
    total: updatedOrder.total,
    currency,
    network: netId,
    address: payAddress,
    qrCode: qr,
    timeout: parseInt(getSetting('payment_timeout') || '60', 10),
    status: 'awaiting_payment'
  });
});

app.post('/api/orders/:id/payment-sent', apiLimiter, async (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'Not found' });
  if (order.status !== 'awaiting_payment') return res.status(400).json({ error: 'Invalid status' });

  db.prepare('UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?').run('awaiting_confirmation', req.params.id);
  const updatedOrder = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id) || { ...order, status: 'awaiting_confirmation' };
  const items = JSON.parse(updatedOrder.items || '[]');

  await sendTelegram(
    buildTelegramOrderMessage(updatedOrder, items, 'review'),
    { inline_keyboard: [[{ text: TG.buttonConfirm, callback_data: `confirm_${req.params.id}` }]] }
  );

  res.json({ ok: true, status: 'awaiting_confirmation' });
});

app.get('/api/orders/:id', (req, res) => {
  const order = db.prepare('SELECT id, status, total, currency, network, tracking_number, created_at, paid_at, shipped_at FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'Not found' });
  res.json(order);
});

app.post('/api/contact', contactLimiter, async (req, res) => {
  const { name, email, subject, message, telegram, whatsapp, lang } = req.body;
  if (!name || !email || !message) return res.status(400).json({ error: 'Missing fields' });

  db.prepare('INSERT INTO contacts(name, email, subject, message, telegram, whatsapp, lang) VALUES(?,?,?,?,?,?,?)')
    .run(name, email, subject || '', message, telegram || '', whatsapp || '', lang || 'en');

  await sendEmail(email, 'Noir Maison Haute', `<div style="background:#0a0a0a;color:#f0ece4;padding:40px;font-family:Georgia,serif"><h2 style="color:#c9a96e;font-weight:300;letter-spacing:3px">NMH</h2><p>Thank you, ${escapeHtml(name)}. We will respond within 24 to 48 hours.</p></div>`, { source: 'contact_autoreply' });

  await sendTelegram(`<b>${TG.contactTitle}</b>\n\n<blockquote>Имя: ${escapeHtml(name)}\nEmail: <code>${escapeHtml(email)}</code>${telegram ? `\nTelegram: <code>${escapeHtml(telegram)}</code>` : ''}${whatsapp ? `\nWhatsApp: <code>${escapeHtml(whatsapp)}</code>` : ''}</blockquote>${subject ? `\n\n<blockquote>Тема: ${escapeHtml(subject)}</blockquote>` : ''}\n\n<blockquote>${escapeHtml(message)}</blockquote>`);

  res.json({ ok: true });
});


const ET = {
  en: { confirmed: 'ORDER CONFIRMED', thanks: 'THANK YOU FOR YOUR PURCHASE', body: 'Your order has been successfully confirmed.', orderNum: 'ORDER #', orderDate: 'DATE', items: 'ITEMS PURCHASED', edp: 'Eau de Parfum', qty: 'Qty', shipping: 'SHIPPING ADDRESS', subtotal: 'Subtotal', shippingL: 'Shipping', total: 'Total', free: 'Free', payment: 'Payment', support: 'For questions, contact us', tagline: 'EXQUISITE FRAGRANCE, PARISIAN ELEGANCE' },
  ru: { confirmed: 'ЗАКАЗ ПОДТВЕРЖДЁН', thanks: 'БЛАГОДАРИМ ЗА ПОКУПКУ', body: 'Ваш заказ успешно подтверждён.', orderNum: 'ЗАКАЗ №', orderDate: 'ДАТА', items: 'СОСТАВ ЗАКАЗА', edp: 'Eau de Parfum', qty: 'Кол во', shipping: 'АДРЕС ДОСТАВКИ', subtotal: 'Подитог', shippingL: 'Дост��вка', total: 'Итого', free: 'Бесплатно', payment: 'Оплата', support: 'Поддержка', tagline: 'ИЗЫСКАННЫЙ АРОМАТ, ПАРИЖСКАЯ ЭЛЕГАНТНОСТЬ' },
  es: { confirmed: 'PEDIDO CONFIRMADO', thanks: 'GRACIAS POR SU COMPRA', body: 'Su pedido ha sido confirmado con éxito.', orderNum: 'PEDIDO #', orderDate: 'FECHA', items: 'ARTÍCULOS', edp: 'Eau de Parfum', qty: 'Cant', shipping: 'DIRECCIÓN DE ENVÍO', subtotal: 'Subtotal', shippingL: 'Envío', total: 'Total', free: 'Gratis', payment: 'Pago', support: 'Soporte', tagline: 'FRAGANCIA EXQUISITA, ELEGANCIA PARISINA' }
};

function getEmailSubject(lang, id) {
  return `NMH: ${(ET[lang] || ET.en).confirmed}: ${id}`;
}

function getProductEmailImage(name) {
  // Uses EMAIL_IMAGE_MAP from catalog.server.js
  for (const [key, envVar] of Object.entries(EMAIL_IMAGE_MAP)) {
    if (name.includes(key) && process.env[envVar]) return process.env[envVar];
  }
  return process.env.EMAIL_HERO_IMAGE || '';
}

function buildSupportButtons(instagram, telegram, whatsapp, email) {
  const items = [];
  if (instagram) items.push({ label: 'Instagram', href: instagram });
  if (telegram)  items.push({ label: 'Telegram',  href: telegram });
  if (email)     items.push({ label: 'Email',     href: `mailto:${email}` });
  if (whatsapp)  items.push({ label: 'WhatsApp',  href: whatsapp });
  if (!items.length) return '';

  const cells = items.map(item => `
    <td align="center" style="padding:4px;">
      <a href="${item.href}" target="_blank" style="display:block;padding:12px 20px;min-width:110px;border:1px solid #2a2520;background:#12100d;color:#c9a96e;text-decoration:none;font-family:Arial,sans-serif;font-size:12px;letter-spacing:1px;text-align:center;">
        ${item.label}
      </a>
    </td>`).join('');

  return `<table role="presentation" cellpadding="0" cellspacing="0" align="center" style="margin:0 auto;"><tr>${cells}</tr></table>`;
}

function buildEmailThumb(url) {
  if (!url) return `<td width="65" height="65" style="width:65px;height:65px;background:#161310;border:1px solid #2a2520;"></td>`;
  return `<td width="65" height="65" background="${url}" style="width:65px;height:65px;background:#161310 url('${url}') center/cover no-repeat;border:1px solid #2a2520;"></td>`;
}

function buildConfirmEmail(order, items) {
  const l = order.lang || 'en';
  const t = ET[l] || ET.en;
  const heroImg = process.env.EMAIL_HERO_IMAGE || getSetting('email_hero_image') || '';
  const supportEmail = getSetting('support_email') || process.env.SUPPORT_EMAIL || 'support@noirmaisonhaute.art';
  const instagram = getSetting('support_instagram') || '';
  const telegram = getSetting('support_telegram') || '';
  const whatsapp = getSetting('support_whatsapp') || '';
  const date = new Date(order.created_at || Date.now()).toLocaleDateString(l === 'ru' ? 'ru-RU' : l === 'es' ? 'es-ES' : 'en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const shippingValue = order.shipping > 0 ? `$${order.shipping}` : t.free;

  const itemRows = items.map(item => {
    const img = getProductEmailImage(item.name);
    return `<tr>${buildEmailThumb(img)}<td style="padding:14px 10px;border-bottom:1px solid #2a2520;vertical-align:top;"><div style="color:#f0ece4;font-size:15px;margin-bottom:3px;">${escapeHtml(item.name)}</div><div style="color:#8a8478;font-size:11px;">${t.edp} ${escapeHtml(item.size || '')} · ${t.qty}: ${item.qty || 1}</div></td><td style="padding:14px 0;border-bottom:1px solid #2a2520;vertical-align:top;text-align:right;"><div style="color:#f0ece4;font-size:17px;">$${item.price * (item.qty || 1)}</div></td></tr>`;
  }).join('');

  const supportButtons = buildSupportButtons(instagram, telegram, whatsapp, supportEmail);
  const heroBlock = heroImg ? `<tr><td height="280" background="${heroImg}" style="height:280px;background:#0d0b09 url('${heroImg}') center/cover no-repeat;line-height:0;font-size:0;">&nbsp;</td></tr>` : '';

  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head><body style="margin:0;padding:0;background:#080808;font-family:Georgia,serif;"><table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#080808;padding:20px 0;"><tr><td align="center"><table width="600" cellpadding="0" cellspacing="0" role="presentation" style="max-width:600px;width:100%;background:#0d0b09;border:1px solid #1e1b16;"><tr><td style="padding:28px 0;text-align:center;border-bottom:1px solid #2a2520;"><div style="font-size:26px;font-weight:300;letter-spacing:10px;color:#c9a96e;">NMH</div></td></tr>${heroBlock}<tr><td style="padding:36px 36px 20px;text-align:center;"><h1 style="font-size:26px;font-weight:400;letter-spacing:3px;color:#f0ece4;margin:0 0 10px;">${t.confirmed}</h1><div style="font-size:11px;letter-spacing:4px;color:#c9a96e;margin-bottom:18px;font-family:Arial,sans-serif;">${t.thanks}</div><p style="font-size:13px;color:#8a8478;line-height:1.7;margin:0;">${t.body}</p></td></tr><tr><td style="padding:0 36px;"><table width="100%" role="presentation" style="border-top:1px solid #2a2520;border-bottom:1px solid #2a2520;"><tr><td style="padding:14px 0;text-align:center;width:50%;font-family:Arial,sans-serif;"><div style="font-size:9px;letter-spacing:2px;color:#5a564e;margin-bottom:3px;">${t.orderNum}</div><div style="font-size:13px;color:#f0ece4;">${escapeHtml(order.id)}</div></td><td style="padding:14px 0;text-align:center;width:50%;border-left:1px solid #2a2520;font-family:Arial,sans-serif;"><div style="font-size:9px;letter-spacing:2px;color:#5a564e;margin-bottom:3px;">${t.orderDate}</div><div style="font-size:13px;color:#f0ece4;">${escapeHtml(date)}</div></td></tr></table></td></tr><tr><td style="padding:28px 36px 0;"><div style="font-size:11px;letter-spacing:4px;color:#c9a96e;text-align:center;margin-bottom:16px;font-family:Arial,sans-serif;">${t.items}</div><table width="100%" role="presentation">${itemRows}</table></td></tr><tr><td style="padding:28px 36px;"><table width="100%" role="presentation"><tr><td style="vertical-align:top;width:50%;font-family:Arial,sans-serif;"><div style="font-size:11px;letter-spacing:3px;color:#c9a96e;margin-bottom:10px;">${t.shipping}</div><div style="font-size:13px;color:#f0ece4;margin-bottom:3px;">${escapeHtml(order.name)}</div><div style="font-size:11px;color:#8a8478;line-height:1.6;">${escapeHtml(order.address || '')}<br>${escapeHtml(order.city || '')}${order.country ? ', ' + escapeHtml(order.country) : ''} ${escapeHtml(order.zip || '')}</div></td><td style="vertical-align:top;width:50%;text-align:right;font-family:Arial,sans-serif;"><table width="100%" role="presentation"><tr><td style="padding:4px 0;font-size:12px;color:#8a8478;">${t.subtotal}</td><td style="padding:4px 0;font-size:12px;color:#f0ece4;text-align:right;">$${order.subtotal}</td></tr><tr><td style="padding:4px 0;font-size:12px;color:#8a8478;">${t.shippingL}</td><td style="padding:4px 0;font-size:12px;color:#f0ece4;text-align:right;">${shippingValue}</td></tr>${order.currency ? `<tr><td style="padding:4px 0;font-size:12px;color:#8a8478;">${t.payment}</td><td style="padding:4px 0;font-size:12px;color:#f0ece4;text-align:right;">${escapeHtml(order.currency)}${order.network ? ` (${escapeHtml(order.network)})` : ''}</td></tr>` : ''}<tr><td colspan="2" style="border-top:1px solid #2a2520;padding:0;"></td></tr><tr><td style="padding:8px 0;font-size:13px;color:#f0ece4;font-weight:bold;">${t.total}</td><td style="padding:8px 0;font-size:20px;color:#c9a96e;text-align:right;">$${order.total}</td></tr></table></td></tr></table></td></tr><tr><td style="padding:28px 36px 8px;text-align:center;border-top:1px solid #2a2520;"><div style="font-size:11px;letter-spacing:3px;color:#c9a96e;margin-bottom:14px;font-family:Arial,sans-serif;">${t.support}</div><p style="font-size:12px;color:#8a8478;margin:0 0 14px;">${supportEmail ? `<a href="mailto:${supportEmail}" style="color:#c9a96e;text-decoration:none;">${escapeHtml(supportEmail)}</a>` : '&nbsp;'}</p>${supportButtons}</td></tr><tr><td style="padding:20px 0;text-align:center;border-top:1px solid #2a2520;"><div style="font-size:9px;letter-spacing:4px;color:#5a564e;font-family:Arial,sans-serif;">${t.tagline}</div></td></tr></table></td></tr></table></body></html>`;
}

function buildShippedEmail(order) {
  const title = order.lang === 'ru' ? 'Заказ отправлен' : order.lang === 'es' ? 'Pedido enviado' : 'Order shipped';
  const tracking = order.tracking_number ? `<p style="text-align:center;margin-top:16px">Tracking: <b style="color:#c9a96e">${escapeHtml(order.tracking_number)}</b></p>` : '';
  return `<div style="background:#0a0a0a;color:#f0ece4;padding:40px;font-family:Georgia,serif;max-width:600px;margin:0 auto"><div style="font-size:28px;letter-spacing:10px;color:#c9a96e;text-align:center;margin-bottom:32px">NMH</div><h2 style="font-weight:300;text-align:center">${title}</h2><p style="text-align:center;color:#8a8478">${escapeHtml(order.id)}</p>${tracking}</div>`;
}

app.get('*', (req, res) => {
  const file = path.join(distDir, 'index.html');
  if (fs.existsSync(file)) {
    res.setHeader('Cache-Control', 'no-cache');
    res.sendFile(file);
  } else {
    res.status(503).send('<html><body style="background:#0a0a0a;color:#f0ece4;font-family:Georgia;display:flex;align-items:center;justify-content:center;height:100vh"><div style="text-align:center"><h1 style="font-weight:300;letter-spacing:4px">NMH</h1><p style="color:#8a8478">Run <code style="color:#c9a96e">npm run build</code></p></div></body></html>');
  }
});

app.listen(PORT, () => {
  console.log(`\n  NOIR MAISON HAUTE`);
  console.log(`  http://localhost:${PORT}`);
  console.log(`  Admin: navigate to /admin`);
  console.log(`  Telegram mode: ${getTelegramMode()}\n`);

  verifyEmailTransport().catch(err => console.error('[EMAIL bootstrap]', err.message));
  bootstrapTelegram().catch(err => console.error('[TG bootstrap]', err.message));
});
