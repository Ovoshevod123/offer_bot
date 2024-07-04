import sqlite3

db = sqlite3.connect('users_offers.db')
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users (
    id integer,
    offer_id_channel text,
    photo text,
    offer_name text,
    description text,
    price text,
    locate text
)""")
# cur.execute(f"INSERT INTO users VALUES (1696788497, 'Kukuru3a', 'class Men(object):',0)")

db.commit()

db.close()