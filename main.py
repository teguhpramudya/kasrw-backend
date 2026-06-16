from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Kas RW API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

class Transaksi(BaseModel):
    tanggal: str
    keterangan: str
    jenis: str
    jumlah: int

@app.get("/")
def read_root():
    return {"message": "Kas RW API berjalan"}

@app.get("/transaksi")
def get_transaksi():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transaksi")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@app.post("/transaksi")
def tambah_transaksi(transaksi: Transaksi):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO transaksi (tanggal, keterangan, jenis, jumlah)
    VALUES (%s, %s, %s, %s)
    """
    values = (
        transaksi.tanggal,
        transaksi.keterangan,
        transaksi.jenis,
        transaksi.jumlah
    )
    cursor.execute(query, values)
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, "message": "Transaksi berhasil ditambahkan"}

@app.get("/transaksi/{id}")
def get_transaksi_by_id(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transaksi WHERE id = %s", (id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    return result