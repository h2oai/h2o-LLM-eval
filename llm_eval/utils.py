import hashlib


def get_sha256(text: str):
    sha256 = hashlib.sha256()
    sha256.update(text.encode("utf-8"))
    shasum = sha256.hexdigest()
    return shasum
