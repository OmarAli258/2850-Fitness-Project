import uuid

users = {}

def register(name, email, password):
    email = email.lower()

    # If email already exists, stop and return nothing
    if email in users:
        return None

    # create the new user
    new_user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password": password
    }

    # save them and return
    users[email] = new_user
    return new_user

def login(email, password):
    email = email.lower()
    user = users.get(email)

    if user is None:
        return None

    # wrong password
    if user["password"] != password:
         return None

    return user

def find_by_id(user_id):
    for user in users.values():
        if user["id"] == user_id:
            return user
    
    return None