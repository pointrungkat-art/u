// Jalankan script ini sekali untuk dapetin JID semua grup WA lo
// Lalu copy JID ke config.json
// Command: node wa_list_groups.js

const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys')

async function listGroups() {
    const { version } = await fetchLatestBaileysVersion()
    const { state, saveCreds } = await useMultiFileAuthState('./wa_session')

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,
        browser: ['PromoBot', 'Chrome', '1.0.0'],
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', async ({ connection }) => {
        if (connection === 'open') {
            console.log('\nConnected! Mengambil daftar grup...\n')
            await new Promise(r => setTimeout(r, 3000))

            const groups = await sock.groupFetchAllParticipating()
            const list   = Object.entries(groups)

            if (list.length === 0) {
                console.log('Tidak ada grup yang ditemukan.')
            } else {
                console.log('='.repeat(50))
                console.log('DAFTAR GRUP WHATSAPP')
                console.log('='.repeat(50))
                list.forEach(([jid, meta]) => {
                    console.log(`Nama  : ${meta.subject}`)
                    console.log(`JID   : ${jid}`)
                    console.log('-'.repeat(50))
                })
                console.log('\nCopy JID yang mau ditarget ke config.json!')
            }

            process.exit(0)
        }
    })
}

listGroups()
