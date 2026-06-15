Авто создание карточек на Wildberries
Сервис собирает карточки товаров из CSV, Google Sheets или таблицы БД, проверяет данные, готовит медиаконтент и отправляет батчи в WB Content API. В режиме DRY_RUN=true карточки только собираются и валидируются.
Возможности
* источники данных: CSV, Google Sheets, PostgreSQL
* маппинг в формат WB: предмет, бренд, характеристики, размеры, баркоды, цвет, описание, цена
* кэш справочников WB через отдельный клиент
* проверка обязательных полей и ограничений до отправки
* загрузка медиа и отправка карточек батчами
* идемпотентность по `vendorCode`
* человекочитаемый отчет по ошибкам API

Формат CSV
```csv
vendor_code,subject_id,subject_name,brand,title,name,description,price,color,country,barcode,size,media_urls
SKU001,1234,Платье,Brand,Летнее платье,Платье миди,Легкая ткань,3490,черный,Россия,4600000000012,44,https://cdn.example.com/1.jpg|https://cdn.example.com/2.jpg
```
Переменные окружения
```env
DATABASE_URL=postgresql+asyncpg://wb_cards:wb_cards@postgres:5432/wb_cards
WB_API_KEY=
SOURCE_TYPE=csv
CSV_PATH=products.csv
DRY_RUN=true
SANDBOX=true
BATCH_SIZE=50
GOOGLE_SHEET_ID=
GOOGLE_CREDENTIALS_JSON=
```
Запуск
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload
```

Через Docker:

```bash
docker compose up --build
```

Запуск публикации:

```bash
curl -X POST http://localhost:8011/runs
```
