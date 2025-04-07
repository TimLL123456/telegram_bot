from database import Database

db = Database()
cursor = db.cursor

def generate_sample_users(num_user=100):

    for i in range(1, num_user + 1):

        user_id = i
        username = f"username_{i}"
        last_name = f"last_name_{i}"
        first_name = f"first_name_{i}"
        created_at = "2023-10-01"
        updated_at = "2023-10-01"


        cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (tg_user_id, created_at, updated_at, tg_username, tg_user_last_name, tg_user_first_name)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, created_at, updated_at, username, last_name, first_name)
        )

        db.conn.commit()

# generate_sample_users(1000)
# print("Sample users generated successfully.")

def update_user_info(user_info:dict):
    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (tg_user_id, updated_at, tg_username, tg_user_last_name, tg_user_first_name)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_info["tg_user_id"],
            user_info["updated_at"],
            user_info["tg_username"],
            user_info["tg_user_last_name"],
            user_info["tg_user_first_name"]
        )
    )
    
    db.conn.commit()


user_info = {
    "tg_user_id": 1,
    "updated_at": "2023-10-02",
    "tg_username": "new_username",
    "tg_user_last_name": "new_last_name",
    "tg_user_first_name": "new_first_name"
}

print("Before update:")
print(db.get_user_by_id(user_info["tg_user_id"]))

update_user_info(user_info)
print("\n\nUser info updated successfully.\n\n")

print("After update:")
print(db.get_user_by_id(user_info["tg_user_id"]))