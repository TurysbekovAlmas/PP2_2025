import os

# Установить все через переменные окружения
os.environ['PGHOST'] = 'localhost'
os.environ['PGPORT'] = '5432'
os.environ['PGDATABASE'] = 'snake_game_db'
os.environ['PGUSER'] = 'postgres'
os.environ['PGPASSWORD'] = 'MyNewPassword123!'
os.environ['PGCLIENTENCODING'] = 'UTF8'

import psycopg2

try:
    # Пустая строка - использует переменные окружения
    conn = psycopg2.connect('')
    
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()
    cursor.execute("SET client_encoding TO 'UTF8';")
    
    cursor.execute("SELECT version();")
    print("✓ PostgreSQL version:", cursor.fetchone()[0][:50])
    
    cursor.execute("SHOW client_encoding;")
    print("✓ Client encoding:", cursor.fetchone()[0])
    
    print("\n✓✓✓ Connection successful! ✓✓✓")
    
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()