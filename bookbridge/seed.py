"""Clearly fictional catalogue records for the local classroom demonstration."""

IDENTITIES = (
    ("customer1", "Demo customer A / 演示顾客甲", "customer"),
    ("customer2", "Demo customer B / 演示顾客乙", "customer"),
    ("staff1", "Demo staff / 演示店员", "staff"),
)

# title, author, category, price in cents, initial available copies
# These invented records represent no real bookstore inventory or customer data.
BOOKS = (
    ("The Quiet Bookshop", "Mira Chen", "Fiction", 3000, 5),
    ("城市里的小书店", "林青", "Fiction", 4200, 8),
    ("A Map of Small Journeys", "Evan Lin", "Travel", 5800, 4),
    ("沿着海岸慢慢走", "许岸", "Travel", 4800, 6),
    ("Python by Small Steps", "Robin Lee", "Technology", 7200, 10),
    ("数据库入门手记", "陈序", "Technology", 6500, 7),
    ("Designing Useful Software", "Alex Wong", "Technology", 8600, 5),
    ("Everyday Algorithms", "Jamie Ho", "Technology", 5400, 3),
    ("一杯茶的时间", "周禾", "Essays", 3600, 12),
    ("Notes from a Window", "May Tan", "Essays", 3900, 9),
    ("The Garden Notebook", "Iris Park", "Nature", 4500, 5),
    ("看得见的四季", "叶森", "Nature", 5200, 6),
    ("Learning to Ask Why", "Sam Yu", "Science", 6900, 4),
    ("星空观察日记", "陆星", "Science", 7800, 2),
    ("Drawing Everyday Things", "Cleo Ma", "Arts", 6200, 7),
    ("色彩与生活", "温彩", "Arts", 5700, 8),
    ("A Little Guide to Study", "Taylor Sun", "Study", 2800, 15),
    ("把问题写下来", "唐问", "Study", 3300, 11),
    ("The Last Paper Boat", "June Lam", "Fiction", 4100, 0),
    ("山间的信", "顾山", "Fiction", 3700, 5),
)


def seed_demo_data(connection, timestamp):
    connection.executemany(
        "INSERT INTO identities (id, name, role) VALUES (?, ?, ?)", IDENTITIES
    )
    connection.executemany(
        """INSERT INTO books
           (title, author, category, price_cents, available_quantity,
            is_listed, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
        [(*book, timestamp, timestamp) for book in BOOKS],
    )
