import bcrypt

class PasswordHasher:
    @classmethod
    def hash(cls, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @classmethod
    def verify(cls, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
