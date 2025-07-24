

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Songs CRUD API")

DB_NAME = "songs.db"

# Modelo de datos
class Song(BaseModel):
    id: int | None = None
    name: str
    path: str
    plays: int = 0

# Inicializa la base de datos y la tabla
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS TBL_SONG (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                plays INTEGER DEFAULT 0
            )
        """)
init_db()

# CRUD

@app.get("/songs", response_model=list[Song])
def get_songs():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT id, name, path, plays FROM TBL_SONG")
        return [Song(id=row[0], name=row[1], path=row[2], plays=row[3]) for row in cur.fetchall()]

@app.get("/songs/{song_id}", response_model=Song)
def get_song(song_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT id, name, path, plays FROM TBL_SONG WHERE id=?", (song_id,))
        row = cur.fetchone()
        if row:
            return Song(id=row[0], name=row[1], path=row[2], plays=row[3])
        raise HTTPException(status_code=404, detail="Song not found")

@app.post("/songs", response_model=Song, status_code=201)
def create_song(song: Song):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            "INSERT INTO TBL_SONG (name, path, plays) VALUES (?, ?, ?)",
            (song.name, song.path, song.plays)
        )
        song.id = cur.lastrowid
        return song

@app.put("/songs/{song_id}", response_model=Song)
def update_song(song_id: int, song: Song):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            "UPDATE TBL_SONG SET name=?, path=?, plays=? WHERE id=?",
            (song.name, song.path, song.plays, song_id)
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Song not found")
        song.id = song_id
        return song

@app.delete("/songs/{song_id}", status_code=204)
def delete_song(song_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("DELETE FROM TBL_SONG WHERE id=?", (song_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Song not found")