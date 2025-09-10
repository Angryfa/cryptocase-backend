# cases/pf_utils.py
import os, hmac, hashlib, base64
from decimal import Decimal, getcontext

getcontext().prec = 28  # чтобы Decimal делился точно

def generate_server_seed() -> str:
    # 32 байта криптостойкой случайности, вернём base64
    return base64.b64encode(os.urandom(32)).decode()

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def hmac_sha256_hex(key: str, msg: str) -> str:
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

def digest_to_uniform(digest_hex: str) -> Decimal:
    # Берём первые 13 hex-символов = 52 бита мантиссы double — равномерно в [0,1)
    n = int(digest_hex[:13], 16)
    return Decimal(n) / Decimal(1 << 52)

def pick_by_weights(r: Decimal, items):
    """
    items: list of dicts [{ "obj": CasePrize, "weight": int }, ...]
    r ∈ [0,1)
    """
    total = sum(max(1, int(i["weight"] or 1)) for i in items)
    if total <= 0:
        total = 1
    cum = Decimal(0)
    for i in items:
        w = Decimal(max(1, int(i["weight"] or 1))) / Decimal(total)
        cum += w
        if r < cum:
            return i["obj"]
    return items[-1]["obj"]
