const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys')
const fs   = require('fs')
const path = require('path')

const CONFIG_FILE = './config.json'
const SESSION_DIR = './wa_session'

let sock     = null
let isReady  = false
const lastSent = {}

function log(msg) {
    const t = new Date().toLocaleTimeString('id-ID')
    console.log(`[${t}] [WA] ${msg}`)
}

function loadConfig() {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'))
}

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms))
}

async function sendToGroup(jid, message) {
    try {
        await sock.sendMessage(jid, { text: message })
        log(`Berhasil kirim ke ${jid}`)
        return true
    } catch (err) {
        log(`Gagal kirim ke ${jid}: ${err.message}`)
        return false
    }
}

async function runScheduler() {
    while (true) {
        if (!isReady) { await sleep(5000); continue }

        const config = loadConfig()
        const groups = config?.whatsapp?.groups || []

        if (groups.length === 0) {
            log('Belum ada grup di config.json!')
            await sleep(60000)
            continue
        }

        const now = Date.now()
        for (const group of groups) {
            const { jid, message, schedule_hours = 6, gap_seconds = 45 } = group

            if (!jid || jid === 'ISI_JID_GRUP_DARI_wa_list_groups') continue
            if (!message) continue

            const last    = lastSent[jid] || 0
            const elapsed = (now - last) / 1000

            if (elapsed >= schedule_hours * 3600) {
                log(`Kirim ke ${jid}...`)
                const ok = await sendToGroup(jid, message)
                if (ok) lastSent[jid] = Date.now()

                // Gap acak antar grup
                const gap = gap_seconds + Math.floor(Math.random() * 20) - 5
                log(`Gap ${gap} detik...`)
                await sleep(gap * 1000)
            }
        }

        await sleep(60000) // cek tiap 1 menit
    }
}

async function connect() {
    const { version } = await fetchLatestBaileysVersion()
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR)

    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,
        browser: ['PromoBot', 'Chrome', '1.0.0'],
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', ({ connection, lastDisconnect }) => {
        if (connection === 'open') {
            log('Connected! Bot siap kirim pesan.')
            isReady = true
        } else if (connection === 'close') {
            isReady = false
            const code = lastDisconnect?.error?.output?.statusCode
            if (code === DisconnectReason.loggedOut) {
                log('Sesi habis. Hapus folder wa_session lalu restart.')
            } else {
                log('Koneksi terputus, reconnecting...')
                setTimeout(connect, 5000)
            }
        }
    })

    // Mulai scheduler
    runScheduler()
}

log('WhatsApp Promo Bot dimulai!')
log('Scan QR code di bawah pakai WA lo...')
connect()
