from database.models import create_db


if __name__ == "__main__":
    create_db()
    print("База даних успішно створена (або оновлена).")
