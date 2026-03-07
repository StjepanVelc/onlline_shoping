# Online Shopping Backend API

Moderan backend za e-commerce aplikaciju izgrađen sa FastAPI, SQLite i Pydantic validacijom.

## Tehnologije

- **FastAPI** - Moderan, brz web framework za Python API
- **SQLite** - Embedded relacijska baza podataka
- **Pydantic** - Validacija podataka i serijalizacija
- **Uvicorn** - ASGI server za pokretanje aplikacije

## Quick Start

### 1. Instalacija virtuelnog okruženja

```powershell
cd C:\Users\Stjepan\onlline_shoping
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalacija zavisnosti

```powershell
pip install -r requirements.txt
```

### 3. Pokretanje servera

```powershell
uvicorn main:app --reload
```

Server pokreće na: `http://127.0.0.1:8000`

### 4. Interaktivna API dokumentacija

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Users (`/users`)
- `POST /users` - Kreiraj novog korisnika
- `GET /users` - Lista korisnika (paginacija, pretraga)
- `GET /users/{id}` - Single korisnik po ID-u
- `PATCH /users/{id}` - Ažuriraj korisnika
- `DELETE /users/{id}` - Obriši korisnika

### Products (`/products`)
- `POST /products` - Kreiraj novi proizvod
- `GET /products` - Lista proizvoda (paginacija, pretraga)
- `GET /products/{id}` - Single proizvod po ID-u
- `PATCH /products/{id}` - Ažuriraj proizvod (cijenu, stock, itd.)
- `DELETE /products/{id}` - Obriši proizvod

### Orders (`/orders`)
- `POST /orders` - Kreiraj novu narudžbu (transakcija sa `order_items`)

## Struktura projekta

```
onlline_shoping/
├── main.py                  # Entry point - importuje app iz data.routes
├── requirements.txt         # Python zavisnosti
├── README.md               # Ova datoteka
│
├── data/
│   ├── base.py            # DB konekcija, init_db(), lifespan, get_db()
│   ├── routes.py          # FastAPI app instance + svi route handlers
│   ├── database.sql       # SQLite schema (auto-izvršava se pri startu)
│   └── shop.db            # SQLite baza (auto-kreira se)
│
├── IO/
│   ├── user.py            # Pydantic modeli za User (Create, Update, Out)
│   ├── product.py         # Pydantic modeli za Product i Order
│   └── admin.py           # Pydantic modeli za Admin (Create, Update, Out)
│
└── repositories/           # [FUTURE] Repository pattern za data access layer
    ├── user_repo.py       # Planned: User CRUD operations
    ├── product_repo.py    # Planned: Product CRUD operations
    └── order_repo.py      # Planned: Order CRUD operations
```

## Baza podataka

SQLite sa 4 tabele:

1. **users** - Korisnici (username, email, country)
2. **products** - Proizvodi (name, description, price, stock)
3. **orders** - Narudžbe (user_id, address, status, total_amount)
4. **order_items** - Stavke narudžbe (order_id, product_id, quantity, price)

Foreign key constraints su uključeni (`ON DELETE CASCADE/RESTRICT`).

### Reset baze podataka

```powershell
Remove-Item data/shop.db -Force
uvicorn main:app --reload
```

Baza će biti automatski kreirana pri prvom startu.

## Razvoj

### Dodavanje novih endpoint-a

1. Kreiraj Pydantic modele u `IO/`
2. Dodaj route handler u `data/routes.py`
3. Testiraj preko `/docs` (Swagger)

### VS Code konfiguracija

- `.vscode/settings.json` - Konfigurisano za SQLite sintaksu
- SQLTools konekcija: `Shop Database` -> direktan pristup bazi iz VS Code-a

## Testiranje

Preko Swagger UI-a (`/docs`):
1. Kreiraj test usera preko `POST /users`
2. Kreiraj proizvod preko `POST /products`
3. Kreiraj order sa `POST /orders` (koristi id-eve iz prethodnih koraka)

## Napomene

- **CORS** je trenutno otvoren za sve (`allow_origins=["*"]`) - za dev svrhe
- **Email validacija** zahtijeva `email-validator` paket (već instaliran)
- Root path (`/`) automatski redirectuje na `/docs`
