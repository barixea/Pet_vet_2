import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("vet_pet.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS animals (
                animal_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                species TEXT NOT NULL,
                breed TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adopters (
                adopter_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adoptions (
                adoption_id TEXT PRIMARY KEY,
                adoption_date TEXT NOT NULL,
                fee_paid REAL NOT NULL,
                animal_id TEXT NOT NULL,
                adopter_id TEXT NOT NULL,
                FOREIGN KEY (animal_id) REFERENCES animals (animal_id),
                FOREIGN KEY (adopter_id) REFERENCES adopters (adopter_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                health_id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id TEXT NOT NULL,
                date_administered TEXT NOT NULL,
                procedure TEXT NOT NULL,
                veterinarian TEXT NOT NULL,
                FOREIGN KEY (animal_id) REFERENCES animals (animal_id)
            )
        """)


def insert_animal(animal_data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO animals (animal_id, name, age, species, breed, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            animal_data["animal_id"],
            animal_data["name"],
            animal_data["age"],
            animal_data["species"],
            animal_data["breed"],
            animal_data["status"]
        ))


def insert_adopter(adopter_data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO adopters (adopter_id, first_name, last_name, age, phone, address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            adopter_data["adopter_id"],
            adopter_data["first_name"],
            adopter_data["last_name"],
            adopter_data["age"],
            adopter_data["phone"],
            adopter_data["address"],
            adopter_data["status"]
        ))


def insert_adoption(adoption_data):
    with get_connection() as conn:
        animal_status_row = conn.execute("""
            SELECT status
            FROM animals
            WHERE animal_id = ?
        """, (adoption_data["animal_id"],)).fetchone()

        if animal_status_row is None:
            raise sqlite3.IntegrityError("Animal ID does not exist.")

        if animal_status_row[0] != "Available":
            raise sqlite3.IntegrityError("Animal is not available for adoption.")

        conn.execute("""
            INSERT INTO adoptions (adoption_id, adoption_date, fee_paid, animal_id, adopter_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            adoption_data["adoption_id"],
            adoption_data["adoption_date"],
            adoption_data["fee_paid"],
            adoption_data["animal_id"],
            adoption_data["adopter_id"]
        ))

        conn.execute("""
            UPDATE adopters
            SET status = ?
            WHERE adopter_id = ?
        """, ("Had Adopted", adoption_data["adopter_id"]))

        conn.execute("""
            UPDATE animals
            SET status = ?
            WHERE animal_id = ?
        """, ("Adopted", adoption_data["animal_id"]))


def insert_health_record(health_data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO health_records (animal_id, date_administered, procedure, veterinarian)
            VALUES (?, ?, ?, ?)
        """, (
            health_data["animal_id"],
            health_data["date_administered"],
            health_data["procedure"],
            health_data["veterinarian"]
        ))


def delete_all_data():
    with get_connection() as conn:
        conn.execute("DELETE FROM adoptions")
        conn.execute("DELETE FROM health_records")
        conn.execute("DELETE FROM adopters")
        conn.execute("DELETE FROM animals")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = ?", ("health_records",))


def fetch_animals():
    with get_connection() as conn:
        return conn.execute("""
            SELECT animal_id, name, age, species, breed, status
            FROM animals
            ORDER BY animal_id
        """).fetchall()


def fetch_adopters():
    with get_connection() as conn:
        return conn.execute("""
            SELECT adopter_id, first_name, last_name, age, phone, address, status
            FROM adopters
            ORDER BY adopter_id
        """).fetchall()


def fetch_adoptions():
    with get_connection() as conn:
        return conn.execute("""
            SELECT adoption_id, adoption_date, fee_paid, animal_id, adopter_id
            FROM adoptions
            ORDER BY adoption_id
        """).fetchall()


def fetch_health_records():
    with get_connection() as conn:
        return conn.execute("""
            SELECT animal_id, date_administered, procedure, veterinarian
            FROM health_records
            ORDER BY health_id
        """).fetchall()


def fetch_animal_ids():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT animal_id
            FROM animals
            ORDER BY animal_id
        """).fetchall()
        return [row[0] for row in rows]


def fetch_available_animal_ids():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT animal_id
            FROM animals
            WHERE status = ?
            ORDER BY animal_id
        """, ("Available",)).fetchall()
        return [row[0] for row in rows]


def fetch_available_adopter_ids():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT adopter_id
            FROM adopters
            WHERE status = ?
            ORDER BY adopter_id
        """, ("Yet to Adopt",)).fetchall()
        return [row[0] for row in rows]
