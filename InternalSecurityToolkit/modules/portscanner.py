"""Port scanner — TCP scan + banner grab + service detect"""
import socket, concurrent.futures, re

COMMON_PORTS = [21,22,23,25,53,80,110,143,443,445,465,587,993,995,
                1433,1521,2181,2375,3000,3306,3389,4243,5432,5601,5672,
                6379,7001,8080,8443,8888,9000,9200,9300,27017,28017]

SERVICE_MAP = {
    21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",
    110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",465:"SMTPS",
    587:"SMTP",993:"IMAPS",995:"POP3S",1433:"MSSQL",1521:"Oracle",
    2181:"Zookeeper",2375:"Docker",3000:"NodeJS/Grafana",3306:"MySQL",
    3389:"RDP",4243:"Docker",5432:"PostgreSQL",5601:"Kibana",
    5672:"RabbitMQ",6379:"Redis",7001:"WebLogic",8080:"HTTP-Alt",
    8443:"HTTPS-Alt",8888:"Jupyter",9000:"SonarQube/MinIO",
    9200:"Elasticsearch",9300:"Elasticsearch",27017:"MongoDB",28017:"MongoDB-HTTP"
}

HIGH_RISK = {2375,2376,6379,27017,9200,5601,8888,9000,4243}

def banner_grab(ip, port, timeout=2):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        try: s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        except: pass
        data = s.recv(256)
        s.close()
        return data.decode(errors='ignore').strip()[:150]
    except: return ""

def scan_port(ip, port, timeout=1.5):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except: return False

def run(target, ports=None, full=False):
    ip = re.sub(r'^https?://','',target).split('/')[0].split(':')[0]
    try: ip = socket.gethostbyname(ip)
    except: pass

    scan_ports = ports if ports else (COMMON_PORTS if not full else list(range(1,10001)))
    findings = []
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as ex:
        results = {ex.submit(scan_port, ip, p): p for p in scan_ports}
        for fut in concurrent.futures.as_completed(results):
            port = results[fut]
            if fut.result():
                open_ports.append(port)

    for port in sorted(open_ports):
        banner = banner_grab(ip, port)
        svc = SERVICE_MAP.get(port, "unknown")
        severity = "HIGH" if port in HIGH_RISK else "LOW"
        entry = {
            "type": "open_port", "port": port,
            "service": svc, "banner": banner,
            "severity": severity,
            "note": f"{'⚠ HIGH RISK — often unauthenticated' if port in HIGH_RISK else ''}"
        }
        findings.append(entry)

    return {"module":"portscanner","target":ip,"open_ports":open_ports,"findings":findings}
