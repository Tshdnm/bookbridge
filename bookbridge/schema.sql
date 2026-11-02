PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS identities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('customer', 'staff'))
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    author TEXT NOT NULL CHECK (length(trim(author)) > 0),
    category TEXT NOT NULL CHECK (length(trim(category)) > 0),
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
    is_listed INTEGER NOT NULL DEFAULT 1 CHECK (is_listed IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stock_receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id),
    staff_id TEXT NOT NULL REFERENCES identities(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL UNIQUE,
    book_id INTEGER NOT NULL REFERENCES books(id),
    customer_id TEXT NOT NULL REFERENCES identities(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    amount_cents INTEGER NOT NULL CHECK (amount_cents = quantity * unit_price_cents),
    status TEXT NOT NULL CHECK (status IN ('Pending collection', 'Completed', 'Cancelled')),
    request_key TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    cancelled_at TEXT,
    UNIQUE (customer_id, request_key)
);

CREATE INDEX IF NOT EXISTS idx_reservations_owner ON reservations(customer_id, id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status, id);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category, is_listed);
