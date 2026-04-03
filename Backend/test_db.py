import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:jgscVhKoOFbdZqbNmEEwOSaWSjxRxmlk@maglev.proxy.rlwy.net:52400/railway",
    sslmode="require"
)

print("Connected!")

from app.core.config import DATABASE_URL
print(DATABASE_URL)