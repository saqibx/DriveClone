# routes/auth_utils.py
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    print(password)
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

def verify_password(stored_password, entered_password):
    return bcrypt.checkpw(entered_password.encode(), stored_password)