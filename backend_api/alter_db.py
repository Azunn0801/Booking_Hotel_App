import sqlite3
c = sqlite3.connect('travel.db')
try:
    c.execute("ALTER TABLE properties ADD COLUMN created_at DATETIME")
    c.commit()
    print('Column created_at added successfully.')
except Exception as e:
    print('Error:', e)
c.close()
