Авто постинг новинок в Instagram и Pinterest
Сервис принимает новинки через webhook или читает их из БД, формирует подпись, хэштеги и ставит публикации в очередь. 
Возможности
* единый интерфейс `Publisher` для площадок
* Instagram Graph API: media container, затем публикация
* Pinterest API v5: создание пина в доску
* расписание и повторные попытки
* дедупликация по паре товар и площадка
* история статусов и ошибок
* REST API для ручного запуска
Переменные окружения
```env
DATABASE_URL=postgresql+asyncpg://social_poster:social_poster@postgres:5432/social_poster
DRY_RUN=true
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_ACCOUNT_ID=
PINTEREST_ACCESS_TOKEN=
PINTEREST_BOARD_ID=
PUBLICATION_SPACING_SECONDS=900
```

Запуск

```bash
pip install -r requirements.txt
uvicorn app.api.main:app --reload
```

Через Docker:

```bash
docker compose up --build
```

Пример webhook:

```bash
curl -X POST http://localhost:8012/webhooks/products \
  -H "Content-Type: application/json" \
  -d '{"product_id":"sku-1","name":"Новая сумка","url":"https://shop.example/sku-1","image_urls":["https://cdn.example/1.jpg"],"price":4200}'
```
