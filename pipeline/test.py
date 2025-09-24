from connect_db_utils import get_connection, query_db

conn = get_connection()

# Count botanists
rows = query_db(conn, "SELECT COUNT(*) FROM beta.Botanist;")
print("Botanists count:", rows[0][0])

# Preview first 5
rows = query_db(conn, "SELECT TOP 5 * FROM beta.Botanist;")
for r in rows:
    print(r)

conn.close()
