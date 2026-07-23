#!/usr/bin/env python3
"""Generate security report PDF for shiroine.web.id"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from datetime import date

OUTPUT = "bugbounty/report-shiroine.web.id.pdf"

# ─── Colors ────────────────────────────────────────────────────────────────────
C_BG       = colors.HexColor("#0D0D0D")
C_RED      = colors.HexColor("#FF2D2D")
C_ORANGE   = colors.HexColor("#FF7A00")
C_YELLOW   = colors.HexColor("#FFD600")
C_GREEN    = colors.HexColor("#00FF88")
C_CYAN     = colors.HexColor("#00E5FF")
C_PURPLE   = colors.HexColor("#A855F7")
C_WHITE    = colors.HexColor("#F0F0F0")
C_GRAY     = colors.HexColor("#888888")
C_DARKGRAY = colors.HexColor("#1A1A1A")
C_PANEL    = colors.HexColor("#111111")

W, H = A4

# ─── Doc ──────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=15*mm, bottomMargin=15*mm,
    title="Security Report — shiroine.web.id",
    author="XC-HACK · Hacking XC Hub",
    subject="Penetration Testing Report",
)

# ─── Styles ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

sTitle = S("sTitle",
    fontName="Helvetica-Bold", fontSize=28, textColor=C_RED,
    alignment=TA_CENTER, spaceAfter=4)

sSubtitle = S("sSubtitle",
    fontName="Helvetica", fontSize=13, textColor=C_CYAN,
    alignment=TA_CENTER, spaceAfter=2)

sMeta = S("sMeta",
    fontName="Helvetica", fontSize=9, textColor=C_GRAY,
    alignment=TA_CENTER, spaceAfter=2)

sH1 = S("sH1",
    fontName="Helvetica-Bold", fontSize=15, textColor=C_CYAN,
    spaceBefore=12, spaceAfter=6)

sH2 = S("sH2",
    fontName="Helvetica-Bold", fontSize=12, textColor=C_ORANGE,
    spaceBefore=8, spaceAfter=4)

sH3 = S("sH3",
    fontName="Helvetica-Bold", fontSize=10, textColor=C_YELLOW,
    spaceBefore=6, spaceAfter=3)

sBody = S("sBody",
    fontName="Helvetica", fontSize=9, textColor=C_WHITE,
    leading=14, alignment=TA_JUSTIFY, spaceAfter=4)

sBodySmall = S("sBodySmall",
    fontName="Helvetica", fontSize=8, textColor=C_WHITE,
    leading=12, spaceAfter=3)

sCode = S("sCode",
    fontName="Courier", fontSize=8, textColor=C_GREEN,
    backColor=C_DARKGRAY, leading=12,
    leftIndent=6, rightIndent=6, spaceAfter=4,
    borderPad=4)

sLabel = S("sLabel",
    fontName="Helvetica-Bold", fontSize=8, textColor=C_GRAY,
    spaceAfter=1)

sBullet = S("sBullet",
    fontName="Helvetica", fontSize=9, textColor=C_WHITE,
    leading=13, leftIndent=12, spaceAfter=2)

sFooter = S("sFooter",
    fontName="Helvetica", fontSize=7.5, textColor=C_GRAY,
    alignment=TA_CENTER)

sCritBadge = S("sCritBadge",
    fontName="Helvetica-Bold", fontSize=10, textColor=C_RED,
    spaceAfter=2)

sHighBadge = S("sHighBadge",
    fontName="Helvetica-Bold", fontSize=10, textColor=C_ORANGE,
    spaceAfter=2)

sMedBadge = S("sMedBadge",
    fontName="Helvetica-Bold", fontSize=10, textColor=C_YELLOW,
    spaceAfter=2)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def HR(color=C_CYAN, thickness=0.5, space=6):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceAfter=space, spaceBefore=space)

def badge_table(severity, fid, title):
    color_map = {"CRITICAL": C_RED, "HIGH": C_ORANGE, "MEDIUM": C_YELLOW}
    c = color_map.get(severity, C_WHITE)
    data = [[
        Paragraph(f"<b>{severity}</b>", ParagraphStyle("b", fontName="Helvetica-Bold",
            fontSize=9, textColor=C_BG)),
        Paragraph(f"<b>[{fid}]</b>", ParagraphStyle("b2", fontName="Helvetica-Bold",
            fontSize=9, textColor=c)),
        Paragraph(f"<b>{title}</b>", ParagraphStyle("b3", fontName="Helvetica-Bold",
            fontSize=9, textColor=C_WHITE)),
    ]]
    t = Table(data, colWidths=[60*mm, 18*mm, None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), c),
        ("BACKGROUND", (1,0), (-1,-1), C_DARKGRAY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("ROUNDEDCORNERS", [4,4,4,4]),
    ]))
    return t

def info_row(label, value, lc=C_GRAY, vc=C_WHITE):
    data = [[
        Paragraph(f"<b>{label}</b>", ParagraphStyle("l", fontName="Helvetica-Bold",
            fontSize=8, textColor=lc)),
        Paragraph(value, ParagraphStyle("v", fontName="Helvetica",
            fontSize=8, textColor=vc)),
    ]]
    t = Table(data, colWidths=[35*mm, None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_PANEL),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return t

# ─── Background Page ──────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # top accent bar
    canvas.setFillColor(C_RED)
    canvas.rect(0, H - 3*mm, W, 3*mm, fill=1, stroke=0)
    # bottom bar
    canvas.setFillColor(C_DARKGRAY)
    canvas.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    canvas.setFillColor(C_GRAY)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(18*mm, 2.5*mm,
        "XC-HACK · Hacking XC Hub · CONFIDENTIAL")
    canvas.drawRightString(W - 18*mm, 2.5*mm,
        f"shiroine.web.id Security Report · 2026-07-19 · Page {doc.page}")
    canvas.restoreState()

# ─── Story ────────────────────────────────────────────────────────────────────
story = []

# ══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 30*mm))

story.append(Paragraph("SECURITY ASSESSMENT REPORT", sTitle))
story.append(Spacer(1, 2*mm))
story.append(Paragraph("shiroine.web.id", sSubtitle))
story.append(HR(C_RED, 1.5, 8))
story.append(Spacer(1, 4*mm))

# Cover meta table
cover_data = [
    ["TARGET",    "shiroine.web.id"],
    ["DATE",      "2026-07-19"],
    ["TEAM",      "XC-HACK · Hacking XC Hub"],
    ["TYPE",      "Black-Box Penetration Test"],
    ["SEVERITY",  "CRITICAL — Immediate Action Required"],
    ["FINDINGS",  "7 total  |  2 Critical  ·  3 High  ·  2 Medium"],
]
cover_table = Table(cover_data, colWidths=[45*mm, None])
cover_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (0,-1), C_DARKGRAY),
    ("BACKGROUND", (1,0), (1,-1), C_PANEL),
    ("TEXTCOLOR", (0,0), (0,-1), C_CYAN),
    ("TEXTCOLOR", (1,0), (1,-1), C_WHITE),
    ("TEXTCOLOR", (1,4), (1,4), C_RED),
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTNAME", (1,0), (1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("GRID", (0,0), (-1,-1), 0.3, C_GRAY),
]))
story.append(cover_table)
story.append(Spacer(1, 10*mm))

story.append(Paragraph(
    "This report documents vulnerabilities discovered during an authorized security assessment "
    "of <b>shiroine.web.id</b>. Findings are classified by severity with detailed impact scenarios "
    "and actionable remediation guidance.",
    sBody))

story.append(Spacer(1, 8*mm))
story.append(HR(C_GRAY, 0.5, 4))
story.append(Paragraph(
    "CONFIDENTIAL — For authorized personnel only. "
    "Do not distribute without permission.",
    sMeta))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("01  EXECUTIVE SUMMARY", sH1))
story.append(HR(C_CYAN, 0.5))

story.append(Paragraph(
    "Pengujian black-box terhadap <b>shiroine.web.id</b> mengungkap <b>7 kerentanan aktif</b> "
    "yang memungkinkan attacker melakukan price manipulation, authentication bypass, "
    "dan eksfiltrasi data sensitif sistem — tanpa memerlukan kredensial valid. "
    "Dua kerentanan Critical berdampak langsung pada integritas finansial dan keamanan akses sistem.",
    sBody))

story.append(Spacer(1, 4*mm))

# Summary table
sum_data = [
    ["Severity", "Count", "Risk Level"],
    ["CRITICAL", "2", "Immediate patch required"],
    ["HIGH",     "3", "Patch within 7 days"],
    ["MEDIUM",   "2", "Patch within 30 days"],
    ["TOTAL",    "7", "—"],
]
sum_table = Table(sum_data, colWidths=[50*mm, 25*mm, None])
sum_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), C_DARKGRAY),
    ("TEXTCOLOR",  (0,0), (-1,0), C_CYAN),
    ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#220000")),
    ("BACKGROUND", (0,2), (-1,2), colors.HexColor("#1A0E00")),
    ("BACKGROUND", (0,3), (-1,3), colors.HexColor("#1A1500")),
    ("BACKGROUND", (0,4), (-1,4), C_PANEL),
    ("TEXTCOLOR",  (0,1), (0,1), C_RED),
    ("TEXTCOLOR",  (0,2), (0,2), C_ORANGE),
    ("TEXTCOLOR",  (0,3), (0,3), C_YELLOW),
    ("TEXTCOLOR",  (0,4), (0,4), C_WHITE),
    ("TEXTCOLOR",  (1,1), (-1,1), C_WHITE),
    ("TEXTCOLOR",  (1,2), (-1,2), C_WHITE),
    ("TEXTCOLOR",  (1,3), (-1,3), C_WHITE),
    ("TEXTCOLOR",  (1,4), (-1,4), C_GRAY),
    ("FONTNAME",   (0,0), (-1,-1), "Helvetica"),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME",   (0,1), (0,-1), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 9),
    ("ALIGN",      (1,0), (1,-1), "CENTER"),
    ("LEFTPADDING",(0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ("GRID",       (0,0), (-1,-1), 0.3, C_GRAY),
]))
story.append(sum_table)
story.append(Spacer(1, 6*mm))

# Risk score
story.append(Paragraph("Overall Risk Score", sH2))
story.append(Paragraph(
    "Berdasarkan scoring CVSS v3.1 dan dampak bisnis, overall risk score sistem ini adalah:",
    sBodySmall))
story.append(Spacer(1, 2*mm))

risk_data = [[
    Paragraph("<b>9.1 / 10</b>", ParagraphStyle("r", fontName="Helvetica-Bold",
        fontSize=22, textColor=C_RED, alignment=TA_CENTER)),
    Paragraph(
        "<b>CRITICAL RISK</b><br/>"
        "Sistem saat ini dalam kondisi dapat dikompromikan secara penuh oleh attacker "
        "tanpa autentikasi. Patch segera pada F-01 dan F-06 diprioritaskan.",
        ParagraphStyle("rd", fontName="Helvetica", fontSize=9,
            textColor=C_WHITE, leading=14)),
]]
risk_table = Table(risk_data, colWidths=[40*mm, None])
risk_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (0,0), colors.HexColor("#1A0000")),
    ("BACKGROUND", (1,0), (1,0), C_DARKGRAY),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 10),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ("BOX", (0,0), (-1,-1), 1, C_RED),
]))
story.append(risk_table)

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# ATTACK CHAIN
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("02  ATTACK CHAIN", sH1))
story.append(HR(C_CYAN, 0.5))

story.append(Paragraph(
    "Rangkaian eksploitasi yang dapat dieksekusi oleh attacker tanpa kredensial apapun:",
    sBody))
story.append(Spacer(1, 3*mm))

chain_steps = [
    ("STEP 1", "Initial Recon", C_GRAY,
     'curl https://shiroine.web.id/api/health\n→ Discover: Midtrans SANDBOX mode active, version info exposed'),
    ("STEP 2", "Auth Bypass (F-06)", C_ORANGE,
     'curl -H "Authorization: Bearer null" https://shiroine.web.id/api/admin/users\n→ 200 OK — bypass auth, akses endpoint proteksi'),
    ("STEP 3", "Data Exfil (F-07)", C_ORANGE,
     '→ Dump owner list + nomor WhatsApp\n→ Lihat statistik internal: 296.884+ pesan, traffic chart'),
    ("STEP 4", "Price Manipulation (F-01)", C_RED,
     'curl -X POST https://shiroine.web.id/api/payment/create-transaction \\\n  -d \'{"package":"premium","amount":1}\'\n→ 200 OK — transaksi Rp1 untuk paket Premium berhasil'),
    ("STEP 5", "Webhook Forge (F-03)", C_RED,
     '→ 10 char pertama signature hash bocor dari error message\n→ Attacker dapat brute-force sisa hash → forge webhook payment success'),
    ("STEP 6", "Server Key Extraction (F-02)", C_RED,
     '→ Prefix + panjang Midtrans server key terekspos di diagnostic\n→ Digunakan untuk forge webhook & direct Midtrans API abuse'),
]

for step_id, step_name, step_color, step_code in chain_steps:
    step_data = [[
        Paragraph(f"<b>{step_id}</b>", ParagraphStyle("si", fontName="Helvetica-Bold",
            fontSize=8, textColor=C_BG, alignment=TA_CENTER)),
        Paragraph(f"<b>{step_name}</b>", ParagraphStyle("sn", fontName="Helvetica-Bold",
            fontSize=9, textColor=step_color)),
    ]]
    st = Table(step_data, colWidths=[20*mm, None])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), step_color),
        ("BACKGROUND", (1,0), (1,0), C_DARKGRAY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether([
        st,
        Paragraph(step_code, sCode),
        Spacer(1, 2*mm),
    ]))

story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "<b>Total Waktu Eksekusi:</b> ~12 menit dari zero knowledge ke full compromise.",
    sBody))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# FINDINGS DETAIL
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("03  FINDINGS DETAIL", sH1))
story.append(HR(C_CYAN, 0.5))

# ─── F-01 ──────────────────────────────────────────────────────────────────
story.append(KeepTogether([
    badge_table("CRITICAL", "F-01", "Unauthenticated Price Manipulation"),
    Spacer(1, 3*mm),
]))

story.append(Paragraph("Deskripsi", sH3))
story.append(Paragraph(
    "Endpoint <b>/api/payment/create-transaction</b> tidak memerlukan autentikasi dan "
    "menerima parameter <b>amount</b> langsung dari request body klien tanpa validasi "
    "sisi-server. Server memproses nilai harga apapun yang dikirimkan client.",
    sBody))

story.append(info_row("CVSS Score", "9.8 (Critical)  —  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", vc=C_RED))
story.append(Spacer(1, 2*mm))

story.append(Paragraph("Proof of Concept", sH3))
story.append(Paragraph(
    'curl -X POST https://shiroine.web.id/api/payment/create-transaction \\\n'
    '  -H "Content-Type: application/json" \\\n'
    '  -d \'{"package": "premium_annual", "amount": 1, "currency": "IDR"}\'\n'
    '# Response: 200 OK — Transaction created, amount: Rp 1',
    sCode))

story.append(Paragraph("Skenario Dampak", sH3))
impacts = [
    "Attacker membeli paket Premium/Annual seharga Rp 1 — kerugian finansial langsung per transaksi.",
    "Abuse massal: bot otomatis membuat ratusan transaksi Rp 1, menguras stok lisensi premium.",
    "Reputasi platform rusak: user legitimate bisa claim layanan premium secara gratis.",
    "Midtrans sandbox mode aktif memperparah: transaksi fake tidak terdeteksi sebagai anomali.",
    "Potential chargeback fraud: attacker dapat order Rp 1, lalu klaim refund via bank.",
]
for i in impacts:
    story.append(Paragraph(f"• {i}", sBullet))

story.append(Paragraph("Solusi & Remediasi", sH3))
solutions = [
    "<b>[IMMEDIATE]</b> Pindahkan validasi harga ke server-side — ambil harga dari database berdasarkan package_id, JANGAN dari request body.",
    "<b>[IMMEDIATE]</b> Tambahkan autentikasi wajib di endpoint create-transaction.",
    "Implementasi rate limiting: maks 3 transaksi per IP per jam.",
    "Verifikasi amount di webhook Midtrans sebelum aktivasi layanan.",
    "Switch Midtrans ke production mode — sandbox tidak boleh live di production.",
    "Audit log semua transaksi dengan anomaly detection untuk harga di luar range normal.",
]
for s in solutions:
    story.append(Paragraph(f"▶  {s}", sBullet))

story.append(Spacer(1, 6*mm))
story.append(HR(C_GRAY, 0.3))
story.append(Spacer(1, 4*mm))

# ─── F-06 ──────────────────────────────────────────────────────────────────
story.append(KeepTogether([
    badge_table("CRITICAL", "F-06", "Broken Authentication — Bearer null Bypass"),
    Spacer(1, 3*mm),
]))

story.append(Paragraph("Deskripsi", sH3))
story.append(Paragraph(
    "Server melakukan validasi autentikasi dengan memeriksa <b>keberadaan</b> header "
    "<b>Authorization</b>, bukan <b>validitas</b> nilai token. Mengirimkan "
    "<code>Authorization: Bearer null</code> atau <code>Authorization: Bearer undefined</code> "
    "berhasil membypass auth check dan mengakses endpoint yang seharusnya terproteksi.",
    sBody))

story.append(info_row("CVSS Score", "9.1 (Critical)  —  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N", vc=C_RED))
story.append(Spacer(1, 2*mm))

story.append(Paragraph("Proof of Concept", sH3))
story.append(Paragraph(
    '# Normal request — 401 Unauthorized\n'
    'curl https://shiroine.web.id/api/admin/users\n\n'
    '# Bypass — 200 OK\n'
    'curl -H "Authorization: Bearer null" https://shiroine.web.id/api/admin/users\n'
    '# Response: {"owners": [...], "stats": {...}}',
    sCode))

story.append(Paragraph("Skenario Dampak", sH3))
impacts2 = [
    "Akses penuh ke semua endpoint admin tanpa password — zero credential required.",
    "Kombinasi dengan F-07: dump seluruh daftar owner + nomor WhatsApp dalam satu request.",
    "Attacker dapat modify/delete data internal jika endpoint write juga menggunakan auth check yang sama.",
    "Statistik bot internal terekspos: traffic pattern, user count, message volume — intelligence untuk targeted attack.",
    "Dapat digunakan sebagai pivot: akses admin endpoint → temukan endpoint sensitif lain.",
]
for i in impacts2:
    story.append(Paragraph(f"• {i}", sBullet))

story.append(Paragraph("Root Cause Analysis", sH3))
story.append(Paragraph(
    "Bug tipikal pada middleware autentikasi yang menggunakan pola:<br/>"
    "<code>if (req.headers.authorization) { /* trust it */ }</code><br/>"
    "alih-alih memvalidasi token secara kriptografis.",
    sBody))

story.append(Paragraph("Solusi & Remediasi", sH3))
solutions2 = [
    "<b>[IMMEDIATE]</b> Validasi token secara kriptografis — verify signature JWT atau lookup token di database.",
    "<b>[IMMEDIATE]</b> Tolak semua nilai token yang bukan valid JWT: null, undefined, empty string, whitespace.",
    "Implementasi middleware terpusat: satu auth function yang digunakan semua endpoint — hindari auth check tersebar.",
    "Unit test wajib untuk auth bypass: test dengan Bearer null, Bearer undefined, Bearer '', dll.",
    "Implementasi token blacklist untuk revokasi token yang dicurigai.",
    "Log semua failed auth attempts dengan IP dan User-Agent untuk deteksi abuse.",
]
for s in solutions2:
    story.append(Paragraph(f"▶  {s}", sBullet))

story.append(PageBreak())

# ─── F-02 ──────────────────────────────────────────────────────────────────
story.append(Paragraph("03  FINDINGS DETAIL (cont.)", sH1))
story.append(HR(C_CYAN, 0.5))

story.append(KeepTogether([
    badge_table("HIGH", "F-02", "Server Key Metadata Leaked in Error Response"),
    Spacer(1, 3*mm),
]))

story.append(Paragraph("Deskripsi", sH3))
story.append(Paragraph(
    "Error response dari server menyertakan informasi diagnostik yang mengungkap "
    "<b>prefix dan panjang</b> Midtrans server key. Informasi ini dapat digunakan "
    "untuk mempersempit ruang brute-force key.",
    sBody))

story.append(info_row("CVSS Score", "7.5 (High)  —  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", vc=C_ORANGE))
story.append(Spacer(1, 2*mm))

story.append(Paragraph("Skenario Dampak", sH3))
impacts3 = [
    "Prefix key + panjang → mempersempit keyspace brute-force dari 10^40 menjadi lebih manageable.",
    "Kombinasi dengan F-03 (signature hash leak): attacker dapat forge webhook Midtrans.",
    "Akses Midtrans API langsung dengan server key → manipulasi status transaksi di dashboard merchant.",
    "Refund fraud: approve refund untuk transaksi yang tidak pernah dibayar.",
]
for i in impacts3:
    story.append(Paragraph(f"• {i}", sBullet))

story.append(Paragraph("Solusi & Remediasi", sH3))
solutions3 = [
    "<b>[URGENT]</b> Rotate Midtrans server key segera — key yang sudah terekspos metadata-nya harus dianggap compromised.",
    "Strip semua informasi sensitif dari error response di production — gunakan generic error messages.",
    "Implementasi error handling terpusat yang memfilter stack trace dan diagnostic info.",
    "Simpan server key di environment variable / secret manager, bukan hardcode di config file.",
    "Aktifkan Midtrans IP whitelist: hanya server IP yang boleh call Midtrans API.",
]
for s in solutions3:
    story.append(Paragraph(f"▶  {s}", sBullet))

story.append(Spacer(1, 4*mm))
story.append(HR(C_GRAY, 0.3))
story.append(Spacer(1, 4*mm))

# ─── F-03 ──────────────────────────────────────────────────────────────────
story.append(KeepTogether([
    badge_table("HIGH", "F-03", "Webhook Signature Hash Partially Leaked"),
    Spacer(1, 3*mm),
]))

story.append(Paragraph("Deskripsi", sH3))
story.append(Paragraph(
    "Error message pada webhook endpoint menyertakan <b>10 karakter pertama</b> dari "
    "expected HMAC-SHA512 signature. Ini memberikan oracle yang dapat digunakan untuk "
    "memverifikasi upaya forging.",
    sBody))

story.append(info_row("CVSS Score", "7.2 (High)  —  AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N", vc=C_ORANGE))
story.append(Spacer(1, 2*mm))

story.append(Paragraph("Skenario Dampak", sH3))
impacts4 = [
    "Signature oracle: attacker mengirim webhook palsu berulang kali, bandingkan 10 char pertama → validasi prefix secara incremental.",
    "Kombinasi F-02 + F-03: dengan prefix key + partial hash → forge full webhook signature.",
    "Inject fake payment notification: mark transaksi sebagai 'paid' tanpa pembayaran nyata.",
    "Mass account upgrade: seluruh user base diupgrade ke premium gratis melalui forged webhook.",
]
for i in impacts4:
    story.append(Paragraph(f"• {i}", sBullet))

story.append(Paragraph("Solusi & Remediasi", sH3))
solutions4 = [
    "<b>[URGENT]</b> Hapus semua informasi signature dari error response — cukup return HTTP 400 tanpa detail.",
    "Implementasi constant-time comparison untuk signature verification — hindari timing oracle.",
    "Whitelist IP Midtrans di level firewall/nginx untuk webhook endpoint.",
    "Log dan alert semua webhook dengan signature invalid — ini indikasi probe oleh attacker.",
    "Implementasi replay attack prevention: reject webhook dengan timestamp lebih dari 5 menit.",
]
for s in solutions4:
    story.append(Paragraph(f"▶  {s}", sBullet))

story.append(Spacer(1, 4*mm))
story.append(HR(C_GRAY, 0.3))
story.append(Spacer(1, 4*mm))

# ─── F-07 ──────────────────────────────────────────────────────────────────
story.append(KeepTogether([
    badge_table("HIGH", "F-07", "Sensitive Data Exposure via Auth Bypass"),
    Spacer(1, 3*mm),
]))

story.append(Paragraph("Deskripsi", sH3))
story.append(Paragraph(
    "Melalui F-06 (Bearer null bypass), attacker dapat mengakses endpoint admin yang "
    "mengembalikan data sensitif: <b>daftar owner & sub-owner</b> beserta nomor WhatsApp, "
    "serta <b>statistik internal bot</b> (296.884+ pesan, traffic pattern).",
    sBody))

story.append(info_row("CVSS Score", "7.5 (High)  —  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N", vc=C_ORANGE))
story.append(Spacer(1, 2*mm))

story.append(Paragraph("Skenario Dampak", sH3))
impacts5 = [
    "Nomor WhatsApp owner/sub-owner terekspos → targeted phishing, SIM swap attack, social engineering.",
    "Traffic pattern internal → attacker mengetahui jam sibuk sistem untuk timing serangan.",
    "Jumlah pengguna aktif (296k+ pesan) → mengestimasi revenue dan nilai target untuk extortion.",
    "Sub-owner list → identify semua akun privileged untuk targeted credential stuffing.",
    "Potensi GDPR/UU PDP violation: data pribadi terekspos tanpa consent.",
]
for i in impacts5:
    story.append(Paragraph(f"• {i}", sBullet))

story.append(Paragraph("Solusi & Remediasi", sH3))
solutions5 = [
    "<b>[IMMEDIATE]</b> Fix F-06 terlebih dahulu — ini prerequisite untuk F-07.",
    "Implement data minimization: admin endpoint hanya return data yang dibutuhkan, bukan full record.",
    "Mask nomor WhatsApp di response: tampilkan hanya 4 digit terakhir.",
    "Pisahkan endpoint statistik internal dari endpoint admin user — gunakan auth level berbeda.",
    "Audit semua endpoint admin untuk data yang tidak perlu dikembalikan.",
]
for s in solutions5:
    story.append(Paragraph(f"▶  {s}", sBullet))

story.append(PageBreak())

# ─── Medium Findings ───────────────────────────────────────────────────────
story.append(Paragraph("03  FINDINGS DETAIL — Medium", sH1))
story.append(HR(C_CYAN, 0.5))

mediums = [
    {
        "id": "F-04", "title": "Midtrans Sandbox Mode Active on Production",
        "cvss": "5.3 (Medium)",
        "desc": "Health endpoint publik mengkonfirmasi payment gateway berjalan di "
                "sandbox mode di environment production. Ini mengindikasikan konfigurasi "
                "yang belum selesai dan memungkinkan transaksi test melewati sistem tanpa deteksi.",
        "impacts": [
            "Transaksi test (fake) dapat diproses tanpa uang nyata berpindah tangan.",
            "Sandbox webhook tidak memiliki proteksi yang sama dengan production — mudah di-forge.",
            "Attacker F-01 diperparah: tidak ada fraud detection Midtrans di sandbox mode.",
            "Potensi confusion antara test data dan production data di dashboard merchant.",
        ],
        "solutions": [
            "<b>[URGENT]</b> Switch ke Midtrans production key segera setelah rotate (lihat F-02).",
            "Implementasi environment check: aplikasi harus crash/refuse start jika prod env tapi sandbox key.",
            "Audit semua transaksi yang terjadi selama sandbox mode aktif.",
            "Implementasi CI/CD check: deployment ke production wajib fail jika MIDTRANS_ENV != 'production'.",
        ],
    },
    {
        "id": "F-05", "title": "Success Page Client-Side Only — No Server Verification",
        "cvss": "5.0 (Medium)",
        "desc": "Halaman sukses pembayaran dapat diakses langsung via URL tanpa server "
                "melakukan verifikasi apakah transaksi benar-benar selesai. "
                "Client-side check saja tidak cukup sebagai gatekeeper.",
        "impacts": [
            "User dapat mengakses success page dan mengklaim 'sudah bayar' padahal belum.",
            "Jika aktivasi layanan dipicu oleh akses success page (bukan webhook), ini bypass payment.",
            "Social engineering: screenshot success page palsu untuk klaim refund atau dispute.",
            "Crawler/bot dapat trigger aktivasi massal dengan hit success page URL.",
        ],
        "solutions": [
            "Pindahkan semua logika aktivasi layanan ke webhook Midtrans — bukan client success redirect.",
            "Success page harus query server untuk verifikasi status transaksi sebelum menampilkan konten.",
            "Implementasi one-time token pada success URL yang expire setelah 15 menit.",
            "Jangan pernah trust client-side untuk keputusan bisnis (aktivasi, upgrade, pembayaran).",
        ],
    },
]

for m in mediums:
    story.append(KeepTogether([
        badge_table("MEDIUM", m["id"], m["title"]),
        Spacer(1, 3*mm),
    ]))

    story.append(Paragraph("Deskripsi", sH3))
    story.append(Paragraph(m["desc"], sBody))
    story.append(info_row("CVSS Score", m["cvss"], vc=C_YELLOW))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("Skenario Dampak", sH3))
    for i in m["impacts"]:
        story.append(Paragraph(f"• {i}", sBullet))

    story.append(Paragraph("Solusi & Remediasi", sH3))
    for s in m["solutions"]:
        story.append(Paragraph(f"▶  {s}", sBullet))

    story.append(Spacer(1, 5*mm))
    story.append(HR(C_GRAY, 0.3))
    story.append(Spacer(1, 4*mm))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# REMEDIATION ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("04  REMEDIATION ROADMAP", sH1))
story.append(HR(C_CYAN, 0.5))

story.append(Paragraph(
    "Prioritas perbaikan berdasarkan severity dan ease of exploitation:",
    sBody))
story.append(Spacer(1, 4*mm))

roadmap_data = [
    ["Priority", "Finding", "Action", "Timeline"],
    ["P0 — NOW",  "F-06", "Fix auth middleware — validate token properly", "< 24 jam"],
    ["P0 — NOW",  "F-01", "Server-side price validation", "< 24 jam"],
    ["P1 — ASAP", "F-02", "Rotate Midtrans key + strip diagnostic errors", "< 48 jam"],
    ["P1 — ASAP", "F-03", "Remove hash from webhook error + IP whitelist", "< 48 jam"],
    ["P1 — ASAP", "F-04", "Switch Midtrans production mode", "< 48 jam"],
    ["P2 — WEEK", "F-07", "Data minimization + mask PII", "< 7 hari"],
    ["P3 — MONTH","F-05", "Server-side success verification", "< 30 hari"],
]

rm_table = Table(roadmap_data, colWidths=[28*mm, 15*mm, None, 22*mm])
priority_colors = {
    "P0 — NOW": C_RED,
    "P1 — ASAP": C_ORANGE,
    "P2 — WEEK": C_YELLOW,
    "P3 — MONTH": C_GREEN,
}
rm_style = [
    ("BACKGROUND", (0,0), (-1,0), C_DARKGRAY),
    ("TEXTCOLOR",  (0,0), (-1,0), C_CYAN),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 8.5),
    ("LEFTPADDING",(0,0), (-1,-1), 6),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ("GRID",       (0,0), (-1,-1), 0.3, C_GRAY),
    ("TEXTCOLOR",  (0,1), (-1,-1), C_WHITE),
    ("BACKGROUND", (0,1), (-1,-1), C_PANEL),
    ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
]
for row_idx, row in enumerate(roadmap_data[1:], 1):
    prio = row[0]
    c = priority_colors.get(prio, C_WHITE)
    rm_style.append(("TEXTCOLOR", (0,row_idx), (0,row_idx), c))
    rm_style.append(("FONTNAME",  (0,row_idx), (0,row_idx), "Helvetica-Bold"))

rm_table.setStyle(TableStyle(rm_style))
story.append(rm_table)

story.append(Spacer(1, 8*mm))

# Quick wins box
story.append(Paragraph("Quick Wins (dapat dilakukan dalam 1 jam)", sH2))
qw = [
    "1. Tambahkan validasi <code>if (!token || token === 'null' || token === 'undefined') return 401;</code> di auth middleware.",
    "2. Pindahkan harga dari request body ke server lookup: <code>const price = PACKAGES[req.body.package_id].price;</code>",
    "3. Set <code>NODE_ENV=production</code> + Midtrans production key.",
    "4. Strip error diagnostic: ganti semua <code>res.json({error, diagnostic})</code> dengan <code>res.json({error: 'Bad request'})</code>",
]
for qw_item in qw:
    story.append(Paragraph(qw_item, sBullet))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# CONCLUSION
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("05  CONCLUSION", sH1))
story.append(HR(C_CYAN, 0.5))

story.append(Paragraph(
    "Sistem <b>shiroine.web.id</b> dalam kondisi kritis dan dapat dikompromikan penuh "
    "oleh attacker dengan skill dasar dalam waktu kurang dari 15 menit. "
    "Dua kerentanan Critical (F-01 dan F-06) harus diperbaiki dalam waktu 24 jam. "
    "Kegagalan memperbaiki dalam timeframe ini berpotensi menyebabkan:",
    sBody))

story.append(Spacer(1, 3*mm))

final_risks = [
    "Kerugian finansial langsung dari price manipulation yang dapat diotomasi.",
    "Eksfiltrasi data personal owner/sub-owner (potensi pelanggaran UU PDP Indonesia).",
    "Kompromi payment infrastructure melalui server key + webhook forging.",
    "Reputasi platform rusak jika eksploitasi menjadi publik.",
]
for r in final_risks:
    story.append(Paragraph(f"⚠  {r}", ParagraphStyle("fr", fontName="Helvetica",
        fontSize=9, textColor=C_ORANGE, leading=14, leftIndent=8, spaceAfter=3)))

story.append(Spacer(1, 6*mm))
story.append(HR(C_GRAY, 0.5))
story.append(Spacer(1, 4*mm))

story.append(Paragraph(
    "Report ini disusun oleh <b>XC-HACK · Hacking XC Hub</b> pada 2026-07-19 "
    "sebagai bagian dari authorized security assessment. Semua temuan telah diverifikasi "
    "secara manual dengan proof-of-concept. Disclosure dilakukan secara responsible.",
    sFooter))

story.append(Spacer(1, 3*mm))
story.append(HR(C_GRAY, 0.3))
story.append(Paragraph(
    "XC-HACK · Hacking XC Hub · pointrungkat-art · 2026",
    sFooter))

# ─── BUILD ────────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"[OK] Report generated: {OUTPUT}")
