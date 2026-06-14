Noir Maison Haute : Perfume E commerce Website
Full stack интернет магазин нишевой парфюмерии. Проект включает витрину товаров, корзину, многошаговое оформление заказа, оплату криптовалютой, личный кабинет, промокоды, письма подтверждения и Telegram уведомления.
Возможности
* Каталог товаров с размерами и ценами.
* Мультиязычный интерфейс: English, Russian, Spanish.
* Корзина.
* Многошаговое оформление заказа.
* Промокоды: процентная скидка и фиксированная скидка.
* Регистрация и вход пользователя.
* Личный кабинет.
* Профиль с адресом.
* История заказов.
* Оплата в разных криптовалютах и сетях.
* Отметка `payment sent`.
* Письма подтверждения заказа через SMTP или Resend API.
* Telegram уведомления о заказах.
* Telegram analytics bot для посещений.
* Contact form.
* Security middleware: helmet, CORS, rate limiting.
* Подбор аромата через короткий опрос.
Стек
 Frontend
* React 18
* Vite
* CSS
Backend
* Node.js
* Express
* better sqlite3
* nodemailer / Resend API
* Telegram Bot API
* helmet
* cors
* express rate limit
* compression
Структура проекта
.
├── src/                   # React-приложение
├── dist/                  # production build
├── db/                    # SQLite database/init scripts
├── server.js              # Express backend
├── catalog.server.js      # backend source of truth для каталога
├── package.json           # npm scripts и зависимости
└── vite.config.js         # Vite config
```
API

| Метод | Endpoint | Описание |
| | | |
| `POST` | `/api/auth/register` | регистрация |
| `POST` | `/api/auth/login` | вход |
| `GET` | `/api/auth/me` | текущий пользователь |
| `PATCH` | `/api/auth/me` | обновить профиль |
| `GET` | `/api/auth/orders` | заказы пользователя |
| `POST` | `/api/promo/validate` | проверка промокода |
| `GET` | `/api/config` | публичная конфигурация магазина |
| `POST` | `/api/orders` | создать заказ |
| `POST` | `/api/orders/:id/pay` | подготовить оплату |
| `POST` | `/api/orders/:id/payment sent` | отметить оплату отправленной |
| `GET` | `/api/orders/:id` | получить заказ |
| `POST` | `/api/contact` | отправить contact form |
| `POST` | `/api/analytics/visit` | записать визит |
| `GET` | `/api/analytics/stats` | статистика посещений |
| `POST` | `/api/telegram/webhook` | Telegram webhook |

Переменные окружения

```env
PORT=3000
SESSION_SECRET=change_me

SUPPORT_EMAIL=
SUPPORT_TELEGRAM=
SUPPORT_INSTAGRAM=
SUPPORT_WHATSAPP=
SUPPORT_X=

SHIPPING_PRICE_USD=20
SHIPPING_FREE_ABOVE=300
SHIPPING_ESTIMATE_DAYS=7-14
PAYMENT_TIMEOUT=30

EMAIL_MODE=smtp
EMAIL_FROM=
SMTP_HOST=
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=
SMTP_PASS=
RESEND_API_KEY=

TELEGRAM_MODE=polling
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_WEBHOOK_URL=
ANALYTICS_BOT_TOKEN=
ANALYTICS_CHAT_ID=

PAY_BTC=
PAY_ETH=
PAY_LTC=
PAY_TRX=
PAY_BNB=
PAY_SOL=
PAY_USDT_TRC20=
PAY_USDT_ERC20=
PAY_USDT_BEP20=
PAY_USDT_POLYGON=
PAY_USDT_SOLANA=
PAY_USDC_ERC20=
PAY_USDC_POLYGON=
PAY_USDC_ARBITRUM=
PAY_USDC_BASE=
PAY_USDC_SOLANA=
```

## Локальный запуск

Установка зависимостей:

```bash
npm install
```

Запуск frontend dev server:

```bash
npm run dev
```

Запуск backend:

```bash
npm start
```

Production build:

```bash
npm run build
npm run preview
```
