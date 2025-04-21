import requests
# 导入beautifulsoup4库
from bs4 import BeautifulSoup
# 引入环境变量 dotenv
from dotenv import load_dotenv
import os
# 加载环境变量
load_dotenv()
# 获取环境变量
account = os.getenv("ACCOUNT")

def rsa_encrypt(modulus_b64, exponent_b64):
    import base64, binascii, requests
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    from Crypto.Util.number import long_to_bytes

    # ---------- 0. 站点公开的 (modulus, exponent) ----------
    # 通常通过解析登录页 JS、hidden input，或抓包得来
    # modulus_b64  = "AMzgM5NXJ1E5YnIxXMRr8ir8J6GyZ6gmj7DA\/OILxvntcrX3R9CGXn8PzE15TrY1WA\/I49\/VFSZI97cN8vJhB\/1m\/eyV1LRHAcCcaCj9\/8nDs2Fg7V0c5zaZCqmXNQovLv1ti3APGkXQF+fbx5IeURgHN3mR29UkaQIukAdT7Fzf"      # 示例：Base64
    # exponent_b64 = "AQAB"                  # 示例：一般就是 0x010001 → "AQAB"

    # ---------- 1. Base64 → int ----------
    def b64_to_int(b64str: str) -> int:
        return int.from_bytes(base64.b64decode(b64str), byteorder="big")

    n_int = b64_to_int(modulus_b64)
    e_int = b64_to_int(exponent_b64)        # 65537

    # ---------- 2. 构造 RSA 公钥对象 ----------
    pub_key = RSA.construct((n_int, e_int))  # 只有 (n, e) 也可以

    # ---------- 3. 前端同款 PKCS#1 v1.5 加密 ----------
    password = os.getenv("PASSWORD")
    password   = password                    # 明文口令
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
    return cipher_b64
session = requests.Session()
url = "https://webvpn.swufe.edu.cn/http/77726476706e69737468656265737421fae0598869237f45780dc7a99c406d361f/xtgl/login_slogin.html?time=1745238581341"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "Cookie":"show_vpn=0; heartbeat=1; show_faq=0; wengine_vpn_ticketwebvpn_swufe_edu_cn=1d5d1cd0d08027d3; route=34a3b7ae344286fc68ba6f863fe092f5; refresh=1"
}
# 发送请求并获取响应
response = session.get(url, headers=headers)
print(response.status_code)
# 创建BeautifulSoup对象
soup = BeautifulSoup(response.text, 'html.parser')
# 获取id为id="csrftoken"的input标签的值
csrftoken = soup.find('input', {'id': 'csrftoken'})['value']
print(csrftoken)

## 获取publick_key
key_url = "https://webvpn.swufe.edu.cn/http/77726476706e69737468656265737421fae0598869237f45780dc7a99c406d361f/xtgl/login_getPublicKey.html?vpn-12-o1-jwxt.swufe.edu.cn&time=1745238581341&_=1745244735691"
key_headers = {
    "Cookie":"show_vpn=0; heartbeat=1; show_faq=0; wengine_vpn_ticketwebvpn_swufe_edu_cn=1d5d1cd0d08027d3; route=34a3b7ae344286fc68ba6f863fe092f5; refresh=1"
}
key_response = session.get(key_url, headers=key_headers)
print(key_response.json())
moudlus = key_response.json()['modulus']
exponent = key_response.json()['exponent']
pwd = rsa_encrypt(moudlus, exponent)
login_body = {
    "csrftoken": csrftoken,
    "language": "zh_CN",
    "ydType": "",
    "yhm":account,
    "mm":pwd,
    "mm":pwd,
}
login_url = "https://webvpn.swufe.edu.cn/http/77726476706e69737468656265737421fae0598869237f45780dc7a99c406d361f/xtgl/login_slogin.html?time=1745238581341"

login_headers = headers

login_response = session.post(login_url, headers=login_headers, data=login_body)
print(login_response.status_code)
print(login_response.text)


# print(soup.prettify())


