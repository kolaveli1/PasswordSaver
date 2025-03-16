import bcrypt
from cryptography.fernet import Fernet

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)

def load_key():
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("Ingen nøgle fundet. Genererer en ny...")
        generate_key()
        return load_key()

def encrypt_password(password):
    key = load_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(password.encode()) 
    return encrypted.decode()

def decrypt_password(encrypted_password):
    key = load_key()
    cipher = Fernet(key)
    
    try:
        encrypted_password_bytes = encrypted_password.encode() if isinstance(encrypted_password, str) else encrypted_password
        decrypted_password = cipher.decrypt(encrypted_password_bytes)
        return decrypted_password.decode()
    except Exception as e:
        print(f"Fejl ved dekryptering: {e}")
        return None

# Master Password Hashing
def hash_master_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_master_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())