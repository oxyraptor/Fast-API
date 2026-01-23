from app.schemas.user import UserCreate

user_db = []

def create_user(user:UserCreate):
    new_user = {
        "id" : len(user_db),
        "name":user.name,
        "email": user.email
        }
    user_db.append(new_user)
    return new_user

def get_all_users():
    return user_db

def get_user_by_id(id:int):
    for user in user_db:
        if user["id"] == id:
            return user
    return False

def update_user_by_id(id:int, user:UserCreate):
    for user in user_db:
        if user["id"] == id:
            user["name"] = user.name
            user["email"] = user.email
            return user
    return False    

def delete_user(user_id: int):
    if user_id >= len(user_db):
        return False
    user_db.pop(user_id)
    return True


