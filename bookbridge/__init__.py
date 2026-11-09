"""BookBridge: a local, sample-data bookstore reservation prototype.

The selectable identities are deliberately a classroom demonstration mechanism,
not a registration or production authentication system.
"""

from decimal import Decimal, InvalidOperation
from functools import wraps
import hmac
from pathlib import Path
import secrets
import sqlite3
from uuid import uuid4

from flask import Flask, g, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException

from .db import close_db, get_db, init_db, timestamp, transaction


PENDING = "Pending collection"
COMPLETED = "Completed"
CANCELLED = "Cancelled"
STATUSES = (PENDING, COMPLETED, CANCELLED)
MAX_QUANTITY = 1_000_000
MAX_PRICE_CENTS = 1_000_000_00


class APIError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def body():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise APIError("Send a JSON object with the required fields.")
    return value


def required_text(value, label, maximum=200):
    if not isinstance(value, str) or not value.strip():
        raise APIError(f"{label} is required.")
    value = value.strip()
    if len(value) > maximum:
        raise APIError(f"{label} must contain at most {maximum} characters.")
    return value


def integer(value, label, minimum=1):
    # JSON 2.0 and True are not accepted as integer quantity inputs.
    if type(value) is not int or not minimum <= value <= MAX_QUANTITY:
        raise APIError(
            f"{label} must be a whole number from {minimum} to {MAX_QUANTITY}."
        )
    return value


def price_cents(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise APIError("Price must be a non-negative amount with at most two decimals.")
    try:
        price = Decimal(str(value).strip())
        if (
            not price.is_finite()
            or price < 0
            or price.as_tuple().exponent < -2
            or price > Decimal(MAX_PRICE_CENTS) / 100
        ):
            raise InvalidOperation
        return int(price * 100)
    except (InvalidOperation, ValueError, OverflowError):
        raise APIError("Price must be from 0 to 1,000,000 with at most two decimals.") from None


def listed_value(value):
    if type(value) is not bool:
        raise APIError("Listing state must be true or false.")
    return int(value)


def require_role(role):
    def decorator(function):
        @wraps(function)
        def guarded(*args, **kwargs):
            if g.identity is None:
                raise APIError("Select a demo identity first.", 401)
            if g.identity["role"] != role:
                raise APIError(f"This action is available to {role} identities only.", 403)
            return function(*args, **kwargs)

        return guarded

    return decorator


def book_record(book_id, connection=None):
    connection = connection or get_db()
    row = connection.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None:
        raise APIError("Book not found.", 404)
    result = dict(row)
    result["is_listed"] = bool(result["is_listed"])
    return result


RESERVATION_SELECT = """
    SELECT r.*, b.title, b.author, i.name AS customer_name
    FROM reservations AS r
    JOIN books AS b ON b.id = r.book_id
    JOIN identities AS i ON i.id = r.customer_id
"""


def reservation_record(reservation_id, connection=None):
    connection = connection or get_db()
    row = connection.execute(
        RESERVATION_SELECT + " WHERE r.id = ?", (reservation_id,)
    ).fetchone()
    if row is None:
        raise APIError("Reservation not found.", 404)
    result = dict(row)
    # The internal replay key does not need to appear in a user's record.
    result.pop("request_key", None)
    return result


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "bookbridge.sqlite"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config.get("SECRET_KEY"):
        secret_path = Path(app.instance_path) / "session-secret.txt"
        try:
            with secret_path.open("x", encoding="ascii") as secret_file:
                secret_file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = secret_path.read_text(encoding="ascii").strip()

    database = app.config["DATABASE"]
    if str(database) != ":memory:":
        Path(database).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    @app.before_request
    def load_identity_and_check_csrf():
        identity_id = session.get("identity_id")
        row = get_db().execute(
            "SELECT id, name, role FROM identities WHERE id = ?", (identity_id,)
        ).fetchone()
        g.identity = dict(row) if row else None
        if request.path.startswith("/api/") and request.method in {"POST", "PATCH", "PUT", "DELETE"}:
            supplied = request.headers.get("X-CSRF-Token", "")
            expected = session.get("csrf_token", "")
            if not expected or not supplied.isascii() or not hmac.compare_digest(supplied, expected):
                raise APIError("Session token is missing or expired. Refresh the page and try again.", 403)

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
            "base-uri 'self'; form-action 'self'"
        )
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(APIError)
    def api_error(error):
        return jsonify(error=error.message), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.exception("Database operation failed")
        return jsonify(error="The local data could not be saved. Please retry the action."), 503

    @app.get("/")
    def index():
        return render_template("index.html")

    def session_response():
        if not session.get("csrf_token"):
            session["csrf_token"] = secrets.token_urlsafe(32)
        identities = get_db().execute(
            "SELECT id, name, role FROM identities ORDER BY id"
        ).fetchall()
        return jsonify(
            identity=g.identity,
            identities=[dict(row) for row in identities],
            csrf_token=session["csrf_token"],
        )

    @app.get("/api/session")
    def read_session():
        return session_response()

    @app.post("/api/session")
    def choose_identity():
        identity_id = body().get("identity_id")
        if not isinstance(identity_id, str):
            raise APIError("Select a valid demo identity.")
        row = get_db().execute(
            "SELECT id, name, role FROM identities WHERE id = ?", (identity_id,)
        ).fetchone()
        if row is None:
            raise APIError("Unknown demo identity.")
        session.clear()
        session["identity_id"] = identity_id
        g.identity = dict(row)
        return session_response()

    @app.get("/api/books")
    def list_books():
        show_unlisted = request.args.get("show_unlisted") == "1"
        if show_unlisted and (not g.identity or g.identity["role"] != "staff"):
            raise APIError("Only staff may view unlisted catalogue records.", 403)
        conditions, values = [], []
        if not show_unlisted:
            conditions.append("is_listed = 1")
        keyword = request.args.get("q", "").strip()
        category = request.args.get("category", "").strip()
        if len(keyword) > 200 or len(category) > 100:
            raise APIError("Search terms are too long.")
        if keyword:
            # Escape SQL wildcard characters so a keyword is searched literally.
            escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            conditions.append("(title LIKE ? ESCAPE '\\' OR author LIKE ? ESCAPE '\\')")
            values.extend([f"%{escaped}%", f"%{escaped}%"])
        if category:
            conditions.append("category = ?")
            values.append(category)
        sorting = {
            "title": "title COLLATE NOCASE, id",
            "price_asc": "price_cents ASC, id",
            "price_desc": "price_cents DESC, id",
        }
        sort = request.args.get("sort", "title")
        if sort not in sorting:
            raise APIError("Sort must be title, price_asc or price_desc.")
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = get_db().execute(
            "SELECT * FROM books" + where + " ORDER BY " + sorting[sort], values
        ).fetchall()
        books = [{**dict(row), "is_listed": bool(row["is_listed"])} for row in rows]
        category_where = "" if show_unlisted else " WHERE is_listed = 1"
        categories = get_db().execute(
            "SELECT DISTINCT category FROM books" + category_where + " ORDER BY category"
        ).fetchall()
        return jsonify(books=books, categories=[row["category"] for row in categories])

    @app.get("/api/books/<int:book_id>")
    def read_book(book_id):
        book = book_record(book_id)
        if not book["is_listed"] and (not g.identity or g.identity["role"] != "staff"):
            raise APIError("Book not found.", 404)
        return jsonify(book=book)

    @app.post("/api/books")
    @require_role("staff")
    def add_book():
        data = body()
        title = required_text(data.get("title"), "Title")
        author = required_text(data.get("author"), "Author")
        category = required_text(data.get("category"), "Category", 100)
        price = price_cents(data.get("price"))
        quantity = integer(data.get("available_quantity"), "Initial quantity", 0)
        listed = listed_value(data.get("is_listed", True))
        now = timestamp()
        with transaction() as connection:
            cursor = connection.execute(
                """INSERT INTO books
                   (title, author, category, price_cents, available_quantity, is_listed, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, author, category, price, quantity, listed, now, now),
            )
            book = book_record(cursor.lastrowid, connection)
        return jsonify(book=book), 201

    @app.patch("/api/books/<int:book_id>")
    @require_role("staff")
    def edit_book(book_id):
        data = body()
        allowed = {"title", "author", "category", "price", "is_listed"}
        if not data or set(data) - allowed:
            raise APIError("Edit title, author, category, price or listing state. Use stock receipts to add copies.")
        updates = {}
        for field in ("title", "author", "category"):
            if field in data:
                updates[field] = required_text(data[field], field.capitalize(), 100 if field == "category" else 200)
        if "price" in data:
            updates["price_cents"] = price_cents(data["price"])
        if "is_listed" in data:
            updates["is_listed"] = listed_value(data["is_listed"])
        updates["updated_at"] = timestamp()
        with transaction() as connection:
            book_record(book_id, connection)
            assignments = ", ".join(f"{key} = ?" for key in updates)
            connection.execute(
                f"UPDATE books SET {assignments} WHERE id = ?", (*updates.values(), book_id)
            )
            book = book_record(book_id, connection)
        return jsonify(book=book)

    @app.post("/api/books/<int:book_id>/receipts")
    @require_role("staff")
    def record_receipt(book_id):
        quantity = integer(body().get("quantity"), "Receipt quantity")
        with transaction() as connection:
            book = book_record(book_id, connection)
            if book["available_quantity"] + quantity > MAX_QUANTITY:
                raise APIError("The resulting available quantity is too large.")
            now = timestamp()
            connection.execute(
                "UPDATE books SET available_quantity = available_quantity + ?, updated_at = ? WHERE id = ?",
                (quantity, now, book_id),
            )
            connection.execute(
                "INSERT INTO stock_receipts (book_id, staff_id, quantity, created_at) VALUES (?, ?, ?, ?)",
                (book_id, g.identity["id"], quantity, now),
            )
            book = book_record(book_id, connection)
        return jsonify(book=book)

    @app.get("/api/reservations")
    def list_reservations():
        if g.identity is None:
            raise APIError("Select a demo identity first.", 401)
        conditions, values = [], []
        if g.identity["role"] == "customer":
            conditions.append("r.customer_id = ?")
            values.append(g.identity["id"])
        status = request.args.get("status", "")
        if status:
            if status not in STATUSES:
                raise APIError("Choose a valid reservation status.")
            conditions.append("r.status = ?")
            values.append(status)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = get_db().execute(RESERVATION_SELECT + where + " ORDER BY r.id DESC", values).fetchall()
        records = []
        for row in rows:
            record = dict(row)
            record.pop("request_key", None)
            records.append(record)
        return jsonify(reservations=records)

    @app.get("/api/reservations/<int:reservation_id>")
    def read_reservation(reservation_id):
        if g.identity is None:
            raise APIError("Select a demo identity first.", 401)
        record = reservation_record(reservation_id)
        if g.identity["role"] == "customer" and record["customer_id"] != g.identity["id"]:
            raise APIError("Reservation not found.", 404)
        return jsonify(reservation=record)

    @app.post("/api/reservations")
    @require_role("customer")
    def reserve_book():
        data = body()
        book_id = integer(data.get("book_id"), "Book identifier")
        quantity = integer(data.get("quantity"), "Reservation quantity")
        key = required_text(data.get("request_key"), "Submission key", 128)
        customer_id = g.identity["id"]
        with transaction() as connection:
            previous = connection.execute(
                "SELECT * FROM reservations WHERE customer_id = ? AND request_key = ?",
                (customer_id, key),
            ).fetchone()
            if previous:
                if previous["book_id"] != book_id or previous["quantity"] != quantity:
                    raise APIError("That submission key belongs to a different reservation.", 409)
                record = reservation_record(previous["id"], connection)
                created = False
            else:
                book = book_record(book_id, connection)
                if not book["is_listed"]:
                    raise APIError("This book is no longer listed for new reservations.", 409)
                if book["available_quantity"] < quantity:
                    raise APIError("Not enough copies are available for that quantity.", 409)
                now = timestamp()
                connection.execute(
                    "UPDATE books SET available_quantity = available_quantity - ?, updated_at = ? WHERE id = ?",
                    (quantity, now, book_id),
                )
                cursor = connection.execute(
                    """INSERT INTO reservations
                       (reference, book_id, customer_id, quantity, unit_price_cents,
                        amount_cents, status, request_key, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    ("BB-" + uuid4().hex[:12].upper(), book_id, customer_id, quantity,
                     book["price_cents"], quantity * book["price_cents"], PENDING, key, now),
                )
                record = reservation_record(cursor.lastrowid, connection)
                created = True
        return jsonify(reservation=record), 201 if created else 200

    @app.post("/api/reservations/<int:reservation_id>/cancel")
    @require_role("customer")
    def cancel_reservation(reservation_id):
        with transaction() as connection:
            record = reservation_record(reservation_id, connection)
            if record["customer_id"] != g.identity["id"]:
                raise APIError("Reservation not found.", 404)
            if record["status"] == COMPLETED:
                raise APIError("A completed reservation cannot be cancelled.", 409)
            if record["status"] == CANCELLED:
                raise APIError("This reservation is already cancelled. Stock has not changed.", 409)
            if record["status"] == PENDING:
                now = timestamp()
                connection.execute(
                    "UPDATE reservations SET status = ?, cancelled_at = ? WHERE id = ?",
                    (CANCELLED, now, reservation_id),
                )
                connection.execute(
                    "UPDATE books SET available_quantity = available_quantity + ?, updated_at = ? WHERE id = ?",
                    (record["quantity"], now, record["book_id"]),
                )
            record = reservation_record(reservation_id, connection)
        return jsonify(reservation=record)

    @app.post("/api/reservations/<int:reservation_id>/complete")
    @require_role("staff")
    def complete_reservation(reservation_id):
        with transaction() as connection:
            record = reservation_record(reservation_id, connection)
            if record["status"] == CANCELLED:
                raise APIError("A cancelled reservation cannot be completed.", 409)
            if record["status"] == COMPLETED:
                raise APIError("This reservation is already completed. Stock and totals have not changed.", 409)
            if record["status"] == PENDING:
                connection.execute(
                    "UPDATE reservations SET status = ?, completed_at = ? WHERE id = ?",
                    (COMPLETED, timestamp(), reservation_id),
                )
            record = reservation_record(reservation_id, connection)
        return jsonify(reservation=record)

    @app.get("/api/summary")
    @require_role("staff")
    def completed_summary():
        row = get_db().execute(
            """SELECT COUNT(*) AS count, COALESCE(SUM(quantity), 0) AS completed_quantity,
                      COALESCE(SUM(amount_cents), 0) AS amount_cents
               FROM reservations WHERE status = ?""",
            (COMPLETED,),
        ).fetchone()
        return jsonify(dict(row))

    return app
