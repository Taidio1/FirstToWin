from pwdlib import PasswordHash

password_hashing_alg = PasswordHash.recommended()


def verify_password(plain_password: str, password_hash: str):
    return password_hashing_alg.verify(plain_password, password_hash)


def hash_password(plain_password: str):
    return password_hashing_alg.hash(plain_password)
