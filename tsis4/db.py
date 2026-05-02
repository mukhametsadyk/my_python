import psycopg2
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_or_create_player(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;", (username,))
    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    p_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return p_id

def save_game_result(p_id, score, level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s);", (p_id, score, level))
    conn.commit()
    cur.close()
    conn.close()

def get_leaderboard():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT p.username, g.score, g.level_reached, g.played_at FROM game_sessions g JOIN players p ON g.player_id = p.id ORDER BY g.score DESC LIMIT 10;")
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

def get_personal_best(p_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s;", (p_id,))
    res = cur.fetchone()[0]
    cur.close()
    conn.close()
    return res if res else 0