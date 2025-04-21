import base64, binascii, requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.number import long_to_bytes

# ---------- 0. 站点公开的 (modulus, exponent) ----------
# 通常通过解析登录页 JS、hidden input，或抓包得来
modulus_b64  = "AMzgM5NXJ1E5YnIxXMRr8ir8J6GyZ6gmj7DA\/OILxvntcrX3R9CGXn8PzE15TrY1WA\/I49\/VFSZI97cN8vJhB\/1m\/eyV1LRHAcCcaCj9\/8nDs2Fg7V0c5zaZCqmXNQovLv1ti3APGkXQF+fbx5IeURgHN3mR29UkaQIukAdT7Fzf"      # 示例：Base64
exponent_b64 = "AQAB"                  # 示例：一般就是 0x010001 → "AQAB"

# ---------- 1. Base64 → int ----------
def b64_to_int(b64str: str) -> int:
    return int.from_bytes(base64.b64decode(b64str), byteorder="big")

n_int = b64_to_int(modulus_b64)
e_int = b64_to_int(exponent_b64)        # 65537

# ---------- 2. 构造 RSA 公钥对象 ----------
pub_key = RSA.construct((n_int, e_int))  # 只有 (n, e) 也可以

# ---------- 3. 前端同款 PKCS#1 v1.5 加密 ----------
password   = "Lihan51938349."                    # 明文口令
cipher     = PKCS1_v1_5.new(pub_key).encrypt(password.encode("utf-8"))

cipher_hex = binascii.hexlify(cipher).decode()
def hex2b64(hexstr: str) -> str:
    b64map   = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    out, i   = [], 0
    while i + 3 <= len(hexstr):
        c = int(hexstr[i:i+3], 16); i += 3
        out.append(b64map[c >> 6] + b64map[c & 63])
    if i + 1 == len(hexstr):
        c = int(hexstr[i:], 16)
        out.append(b64map[c << 2])
    elif i + 2 == len(hexstr):
        c = int(hexstr[i:], 16)
        out.append(b64map[c >> 2] + b64map[(c & 3) << 4])
    while len("".join(out)) % 4: out.append("=")
    return "".join(out)

cipher_b64 = hex2b64(cipher_hex)
# ---------- 4. 输出格式：Base64（与 hex2b64 等价） ----------
# cipher_b64 = base64.b64encode(cipher).decode()

print("最终密文 =", cipher_b64)

# # ---------- 5. 构造并发送请求 ----------
# login_url = "https://example.com/login"
# payload   = {
#     "mm": cipher_b64,    # 密码字段
#     "user": "alice"      # 其他字段...
# }
# session = requests.Session()
# resp = session.post(login_url, data=payload, timeout=8)
# print("响应码:", resp.status_code)