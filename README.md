 NPL x AppTak Integration — Backend & Mock Frontend

Internship project for **Muller & Phipps Company Private Limited**, building the backend integration between the Nouveaux Pharma Limited (NPL) website and the DawaAppTak/AppTak platform.


 What This Is

Per the project brief, this implements the backend structure and logic for:
- A NPL product listing with "Add to Cart" that hands off to an AppTak-style gateway
- A shopping cart system
- An order/checkout flow
- A backend-configurable discount and pricing engine (product price, discount %, promo codes, validity dates, eligibility)

Since access to AppTak's real production source code was intentionally not granted at this stage, this project builds an **authentic, fully-working backend** (real database schema, real business logic, real API) behind a **mock frontend** standing in for NPL's and AppTak's real pages. The intent is for this backend logic to be reviewed and then adapted directly into the real AppTak (Laravel) codebase.

 Tech Stack

- **Backend:** PHP 8 / Laravel
- **Database:** MySQL
- **Frontend (mock):** Plain HTML/CSS/vanilla JS (Blade view), matching AppTak's confirmed Laravel/Blade stack

## Database Schema

| Table | Purpose |
|---|---|
| `products` | NPL product catalog (name, SKU, price, description) |
| `customers` | Customer/patient accounts |
| `carts` / `cart_items` | Active shopping carts and their line items |
| `discount_rules` | Admin-configurable pricing/discount/promo rules |
| `orders` / `order_items` | Completed orders with final pricing after discounts |

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST/PUT/DELETE | `/api/products` | Product CRUD |
| GET/POST/PUT/DELETE | `/api/customers` | Customer CRUD |
| GET/POST/PUT/DELETE | `/api/discount-rules` | Discount/promo rule CRUD |
| POST | `/api/carts` | Add a product to cart ("Add to Cart") |
| GET | `/api/carts/{id}` | View a cart |
| POST | `/api/carts/{id}/handoff` | Hand off cart to AppTak gateway (mocked) |
| DELETE | `/api/carts/{id}` | Delete a cart |
| POST | `/api/orders` | Complete an order from a cart, applying a discount rule if provided |
| GET | `/api/orders/{id}` | View an order |
| PATCH | `/api/orders/{id}` | Update order status |

 Local Setup

1. Clone the repo
2. `composer install`
3. Copy `.env.example` to `.env` and set your `DB_*` values
4. `php artisan key:generate`
5. `php artisan migrate`
6. Visit the app root (`/`) for the mock NPL product page

 Not Yet Implemented

- Admin panel UI for managing discount rules and pricing without direct API calls
- Real integration with AppTak's production backend (pending access/approval)
- Customer authentication flow (Sanctum installed, not yet wired to endpoints)

ALL DONE NOW ONLY SOURCE COD EINTEGRATION IS PENDING
