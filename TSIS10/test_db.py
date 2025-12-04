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
    """-- Посмотреть все таблицы
\dt

-- Структура таблицы users
\d users

-- Структура таблицы phones
\d phones

-- Все пользователи
SELECT * FROM users;

-- Все телефоны
SELECT * FROM phones;

-- Контакты с телефонами (JOIN)
SELECT u.user_id, u.first_name, u.last_name, u.email, 
       p.phone_number, p.phone_type, p.is_primary
FROM users u
LEFT JOIN phones p ON u.user_id = p.user_id
ORDER BY u.last_name, u.first_name;

-- Подсчет телефонов у каждого контакта
SELECT u.first_name, u.last_name, COUNT(p.phone_id) as phone_count
FROM users u
LEFT JOIN phones p ON u.user_id = p.user_id
GROUP BY u.user_id, u.first_name, u.last_name
ORDER BY phone_count DESC;

-- Выйти
\q
Snake Game DB Queries
SELECT u.username, us.level, us.score, us.high_score, us.last_played
FROM users u
JOIN user_scores us ON u.user_id = us.user_id;"""