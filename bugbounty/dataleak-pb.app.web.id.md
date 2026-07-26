# Data Leak Report — BimaSoft / pb.app.web.id

> Scraped via `tools/dataleak.py` — DataLeak Scanner
> Target: `pb.app.web.id` (PocketBase backend)
> Date: 2026-07-22
> Status: **ALL DATA ACCESSIBLE WITHOUT AUTHENTICATION**

---

## Summary

| Collection | Total Records | Sampled | Key Data |
|------------|---------------|---------|----------|
| DataUsers | **1,824** | 50 | Email guru + kode sekolah + logo |
| DataUjian | **4,680** | 50 | Kode ujian + jadwal + email guru |
| DataPengawas | **1** | 1 | Nama + username + **PASSWORD PLAINTEXT** |
| DataJawaban | **13** | 13 | Jawaban siswa + skor + mapel |
| DataKunci | **1** | 1 | Kunci jawaban (encrypted) |

---

## DataPengawas — Plaintext Credentials

| Field | Value |
|-------|-------|
| `id` | `q782q2q6k187oui` |
| `nama` | `Nurul Farida` |
| `username` | `Nurul` |
| `password` | `Nurul12345` |
| `namespace` | `` |
| `key` | `:Nurul` |
| `created` | `2026-03-30 03:48:59.777Z` |
| `updated` | `2026-03-30 03:48:59.777Z` |

> **CRITICAL**: Password stored in plaintext — `Nurul12345`

---

## DataUsers — Teacher/School Accounts (sample 50 of 1,824)

| # | Username | Email (namespace) | Nama Sekolah | Logo |
|---|----------|-------------------|--------------|------|
| 1 | `CBTMYID` | `yokowasis@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 2 | `457667` | `slamet16@guru.smp.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 3 | `279126` | `mahlispd55@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 4 | `728277` | `iwan.wr@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 5 | `227307` | `mtssalfalahlemahabang@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 6 | `609471` | `transferrespon27@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 7 | `483551` | `setiwandali@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 8 | `156708` | `agungrakapraktyasa@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 9 | `236836` | `tikinacolo123@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 10 | `653442` | `budi.setyono13@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 11 | `SMKS YAPIS FF` | `kecebrother86@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 12 | `498840` | `ahmadkohar067@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 13 | `724468` | `denkakak71@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 14 | `199192` | `sukamaramis@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 15 | `550724` | `m.ilmi657@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 16 | `783966` | `yudhifiyyah@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 17 | `527457` | `daffajunior359@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 18 | `MAN 1 KOTA BIMA` | `info@man1kotabima.sch.id` | MAN 1 KOTA BIMA | https://i0.wp.com/upload.wikimedia.or... |
| 19 | `895569` | `mtsnduatasikmalaya@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 20 | `610065` | `siswa@man1kotabima.sch.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 21 | `508283` | `moch.ikhsan.s23@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 22 | `421214` | `kurikulumnepur2025@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 23 | `963852` | `hallobaksor@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 24 | `137946` | `saefullahasep1933@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 25 | `449818` | `guruhmunawar97@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 26 | `612271` | `mtss.alkhairat90321@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 27 | `253846` | `dokumentasiskanuha@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 28 | `589104` | `mtssal.khairat321@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 29 | `996486` | `kadekwirahadi24@guru.smp.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 30 | `300540` | `misnurulfatah92@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 31 | `415252` | `citracinta.030383@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 32 | `877677` | `fannyfes7@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 33 | `578504` | `purnawansyah54@admin.sma.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 34 | `773264` | `hielmybudhiman@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 35 | `958057` | `lindasmodi@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 36 | `819771` | `opsman13mm@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 37 | `348844` | `imalamoalfiki@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 38 | `138933` | `nasrul.fazri4@guru.sma.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 39 | `749112` | `ndzm2.diantega@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 40 | `435185` | `susimariesta7@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 41 | `324137` | `nasrulfazri39@guru.smp.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 42 | `577839` | `yose.hermanto01@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 43 | `397241` | `us.smansalumbis@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 44 | `165569` | `muchlispalar2019@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 45 | `114882` | `ansorifikri@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 46 | `983329` | `7umadi27@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 47 | `405552` | `robertpasaribu86@guru.smp.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 48 | `SMAN 1 PLAU TIMUR` | `englishberangas@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 49 | `906242` | `ilhammaulanaaa208@gmail.com` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |
| 50 | `489273` | `eduardussebatu42@guru.sma.belajar.id` | BIMASOFT | https://i0.wp.com/snipboard.io/wRL8GN... |

---

## DataUjian — Exam Records (sample 50 of 4,680)

| # | Kode | Key (Email) | Kelas | Jumlah Soal | Alokasi | Tanggal | Jam |
|---|------|-------------|-------|-------------|---------|---------|-----|
| 1 | `JENIS - JENIS SOAL 2` | `yokowasis@cbt.my.id:JENIS - JENIS SOAL 2` | 64,65 | 20 | 50 | 2025-04-05 | 17:46 |
| 2 | `UJI COBA` | `agungrakapraktyasa@gmail.com:UJI COBA` | X | 2 | 120 | 2025-05-14 | 15:08 |
| 3 | `PSAJIPA_2025` | `saefullahasep1933@gmail.com:PSAJIPA_2025` | GURU | 40 | 60 | 2025-05-20 | 07:30 |
| 4 | `FISIKA_ASAS` | `transferrespon27@gmail.com:FISIKA_ASAS` | X;XI;XII | 3 | 5 | 20025-05-19 | 10:00 |
| 5 | `UJI COBA` | `mtssal.khairat321@gmail.com:UJI COBA` | 5 | 3 | 120 | 2025-05-19 | 09:24 |
| 6 | `SOAL 2` | `mtssal.khairat321@gmail.com:SOAL 2` | 5 | 1 | 120 | 2025-05-19 | 09:55 |
| 7 | `Hortatory Exposition` | `setiwandali@gmail.com:Hortatory Exposition` | XI | 5 | 90 | 2025-05-19 | 13:24 |
| 8 | `SOAL IPA KELAS V` | `sukamaramis@gmail.com:SOAL IPA KELAS V` | V/A;V/B | 40 | 60 | 2025-05-19 | 16:49 |
| 9 | `SOAL SUSAH` | `sukamaramis@gmail.com:SOAL SUSAH` | V/A;V/B | 3 | 60 | 2025-05-19 | 17:00 |
| 10 | `UJI COBA` | `setiwandali@gmail.com:UJI COBA` | XI | 5 | 11 | 2025-05-21 | 21:53 |
| 11 | ` IPS` | `imalamoalfiki@gmail.com: IPS` | VIII | 25 | 90 | 2025-05-27 | 09:30 |
| 12 | `TES SOAL` | `muchlispalar2019@gmail.com:TES SOAL` | 10A-IS | 2 | 10 | 2025-05-22 | 08:50 |
| 13 | `TKJ` | `ilhammaulanaaa208@gmail.com:TKJ` | X TKJ  | 1 | 2 | 2025-05-23 | 13:38 |
| 14 | `Kisi Kisi Mulok XI RPL B` | `akunsultanpunya6666@gmail.com:Kisi Kisi Mulok XI RPL B` | XI-RPL-B | 20 | 60 | 2025-05-23 | 07:00 |
| 15 | `A` | `kristel.tumanggor@gmail.com:A` | X | 5 | 60 | 2025-05-23 | 11:12 |
| 16 | `UJIAN BAHASA INGGRIS KELAS XI` | `opsman13mm@gmail.com:UJIAN BAHASA INGGRIS KELAS XI` | XI B;XI C | 25 | 120 | 2025-06-10 | 07:30 |
| 17 | `UJIAN TIK KELAS X` | `opsman13mm@gmail.com:UJIAN TIK KELAS X` | X B;X C | 20 | 120 | 2025-06-03 | 09:00 |
| 18 | `SOAL FISIKA KELAS X` | `opsman13mm@gmail.com:SOAL FISIKA KELAS X` | X A;X B;X C | 25 | 120 | 2025-06-02 | 07:30 |
| 19 | `UJI COBA SOAL` | `rifqinajahi33@gmail.com:UJI COBA SOAL` | 8A;9A | 5 | 30 | 2025-05-27 | 00:38 |
| 20 | `UJI COBA TES` | `yuliruslina87@admin.smp.belajar.id:UJI COBA TES` | 7 | 1 | 2 | 2025-05-28 | 20:45 |
| 21 | `PAIBP` | `sdn05asparaga@gmail.com:PAIBP` | VI | 5 | 120 | 2025-05-31 | 22:16 |
| 22 | `AKIDAH AKHLAK Kls 8(1,3,4,5)` | `fauzyalfaruq52@gmail.com:AKIDAH AKHLAK Kls 8(1,3,4,5)` | VIII.1;VIII.3;VIII.4;VIII.5 | 30 | 60 | 2025-06-02 | 08:40 |
| 23 | `AKIDAH AKHLAK kelas 8.2` | `fauzyalfaruq52@gmail.com:AKIDAH AKHLAK kelas 8.2` | VIII.2 | 30 | 60 | 2025-06-02 | 08:41 |
| 24 | `AKIDAH AKHLAK 7 (1,2,3,4,5,6)` | `fauzyalfaruq52@gmail.com:AKIDAH AKHLAK 7 (1,2,3,4,5,6)` | VII.1;VII.2;VII.3;VII.4;VII.5;VII.6 | 30 | 60 | 2025-06-02 | 08:40 |
| 25 | `TIK X` | `sultonsatusatu@gmail.com:TIK X` | X | 4 | 50 | 2025-06-02 | 00:33 |
| 26 | `SOAL SIMULASI` | `tu.yasmieen@gmail.com:SOAL SIMULASI` | VII | 10 | 60 | 2025-06-02 | 07:00 |
| 27 | `INFORMATIKA X` | `imarismail81@gmail.com:INFORMATIKA X` | X-TPM | 10 | 120 | 2025-06-04 | 21:52 |
| 28 | `PSAT EKONOMI 10` | `agung.gunawan5759@guru.smp.belajar.id:PSAT EKONOMI 10` | 10 | 50 | 90 | 2025-06-05 | 14:00 |
| 29 | `PSAT INFORMATIKA 10` | `agung.gunawan5759@guru.smp.belajar.id:PSAT INFORMATIKA 10` | 10 | 50 | 120 | 2025-06-10 | 14:00 |
| 30 | `PSAT EKONOMI 11` | `agung.gunawan5759@guru.smp.belajar.id:PSAT EKONOMI 11` | 11 | 50 | 120 | 2025-06-05 | 14:00 |
| 31 | `PSAT PAI 10` | `agung.gunawan5759@guru.smp.belajar.id:PSAT PAI 10` | 10 | 40 | 120 | 2025-06-03 | 13:00 |
| 32 | `INFORMATIKA SMK` | `imarismail81@gmail.com:INFORMATIKA SMK` | X-TBSM | 20 | 240 | 2025-06-20 | 08:00 |
| 33 | `BK` | `zainalmanik86@gmail.com:BK` | VIII | 4 | 90 | 2025-06-04 | 01:00 |
| 34 | `UJI COBA SOAL` | `rw03gapas28@gmail.com:UJI COBA SOAL` | X-1 BDP;X-2 BDP;XI BDP | 5 | 120 | 2025-06-04 | 10:25 |
| 35 | `ULANGAN HARIAN` | `wijayagerrald21@gmail.com:ULANGAN HARIAN` | 4 | 5 | 60 | 2025-04-06 | 11:20 |
| 36 | `10-FISIKA-SAS2025-2` | `digitalsinergi51@gmail.com:10-FISIKA-SAS2025-2` | X | 35 | 90 | 2025-06-04 | 21:28 |
| 37 | `SIMULASI_PSAT_2025` | `email.smpn3cikarangtimur@gmail.com:SIMULASI_PSAT_2025` | KELAS PAI | 25 | 60 | 2025-06-07 | 06:04 |
| 38 | `PAIBP KELAS X PAT` | `rw03gapas28@gmail.com:PAIBP KELAS X PAT` | X-1 BDP;X-2 BDP | 40 | 100 | 2025-06-10 | 07:30 |
| 39 | `PAIBP KELAS XI PAT` | `rw03gapas28@gmail.com:PAIBP KELAS XI PAT` | XI BDP | 40 | 100 | 2025-06-10 | 07:30 |
| 40 | `BING KELAS X PAT` | `rw03gapas28@gmail.com:BING KELAS X PAT` | X-1 BDP;X-2 BDP | 40 | 100 | 2025-06-10 | 09:00 |
| 41 | `PB KELAS X PAT` | `rw03gapas28@gmail.com:PB KELAS X PAT` | X-1 BDP;X-2 BDP | 35 | 100 | 2025-06-10 | 10:45 |
| 42 | `PP KELAS XI PAT` | `rw03gapas28@gmail.com:PP KELAS XI PAT` | XI BDP | 40 | 100 | 2025-06-10 | 10:45 |
| 43 | `BING KELAS XI PAT` | `rw03gapas28@gmail.com:BING KELAS XI PAT` | XI BDP | 40 | 100 | 2025-06-10 | 09:00 |
| 44 | `BINDO KELAS XI PAT` | `rw03gapas28@gmail.com:BINDO KELAS XI PAT` | XI BDP | 40 | 100 | 2025-06-11 | 07:30 |
| 45 | `PJOK KELAS X PAT` | `rw03gapas28@gmail.com:PJOK KELAS X PAT` | X-1 BDP;X-2 BDP | 40 | 100 | 2025-06-11 | 09:00 |
| 46 | `PJOK KELAS XI PAT` | `rw03gapas28@gmail.com:PJOK KELAS XI PAT` | XI BDP | 40 | 100 | 2025-06-11 | 09:00 |
| 47 | `PKK KELAS XI PAT` | `rw03gapas28@gmail.com:PKK KELAS XI PAT` | XI BDP | 40 | 100 | 2025-06-11 | 10:40 |
| 48 | `BINDO KELAS X PAT` | `rw03gapas28@gmail.com:BINDO KELAS X PAT` | X-1 BDP;X-2 BDP | 40 | 100 | 2025-06-11 | 10:00 |
| 49 | `SKD KELAS X PAT` | `rw03gapas28@gmail.com:SKD KELAS X PAT` | X-1 BDP;X-2 BDP | 15 | 240 | 2025-06-11 | 10:40 |
| 50 | `MTK KELAS X PAT` | `rw03gapas28@gmail.com:MTK KELAS X PAT` | X-1 BDP;X-2 BDP | 35 | 120 | 2025-06-12 | 07:30 |

---

## DataJawaban — Student Answers (all 13 records)

| # | Username | Mapel | Status | Waktu Selesai | Jawaban (truncated) |
|---|----------|-------|--------|---------------|---------------------|
| 1 | `` |  | mengerjakan |  | `` |
| 2 | `U06966` | 28 FISIKA XI ASAS GANJIL 2025 | selesai | 2025-11-28T01:23:12.543Z | `{"1":"B","2":"C","3":"A","4":"C","5":"B","6":"E...` |
| 3 | `12343` | SEJARAH KELAS XI | selesai | 2025-12-01T02:25:07.837Z | `{"1":"B","2":"B","3":"A","4":"C","5":"E","6":"C...` |
| 4 | `12036` | FISIKA_XII B1,B2,D1,D2 | selesai | 2025-12-03T04:09:10.215Z | `{"1":"C","2":"C","3":"B","4":"B","5":"C","6":"B...` |
| 5 | `149BSAS478` | PP 9 SIANG PSAS GJL 2526 | selesai | 2025-12-03T09:39:24.696Z | `{"1":"A","2":"D","3":"A","4":"A","5":"D","6":"A...` |
| 6 | `ASA-377` | PPKN | selesai | 2026-03-10T03:19:27.219Z | `{"1":"B","2":"C","3":"D","4":"C","5":"A","6":"D...` |
| 7 | `0103756171` | FIQIH_MTSN12PESSEL_ESSAY | selesai | 2026-04-30T03:14:13.495Z | `{"waktuMulai":"2026-04-30T03:02:37.093Z","waktu...` |
| 8 | `0113841829` | 31_PP_ASAJ_2026 | selesai | 2026-05-04T04:08:24.095Z | `{"1":"B","2":"B","3":"C","4":"B","5":"B","6":"B...` |
| 9 | `105182200` | ASAJ- BAHASA REJANG  IX 2026 | selesai | 2026-05-09T01:38:10.321Z | `{"1":"C","2":"C","3":"C","4":"A","5":"C","6":"C...` |
| 10 | `0136765977` | Bahasa Jawa | selesai | 2026-05-09T02:45:48.424Z | `{"1":"C","2":"B","3":"B","4":"C","5":"D","6":"A...` |
| 11 | `132078318` | 7_QH_MTSN12PESSEL_ESSAY | selesai | 2026-06-02T03:10:40.747Z | `{"waktuMulai":"2026-06-02T02:42:12.845Z","waktu...` |
| 12 | `0116890516` | 31_BIN_ASAT_8_2026 | selesai | 2026-06-08T01:35:44.645Z | `{"1":"B","2":"D","3":"B","4":"A","5":"D","6":"B...` |
| 13 | `0123230453` | 31_BSUND_ASAT7_2026 | selesai | 2026-06-12T03:02:14.249Z | `{"1":"D","2":"A","3":"A","4":"C","5":"D","6":"C...` |

---

## DataKunci — Answer Key (1 record)

| Field | Value |
|-------|-------|
| `id` | `6x1abdqv66is1f6` |
| `kode` | `SIMULASI KLS 6` |
| `namespace` | `` |
| `key` | `null:SIMULASI KLS 6` |
| `created` | `2025-11-20 11:44:47.031Z` |
| `kunci` | `luf0gzlo+nirtz+0F/FHCsC5vC3tKGtIbyQe3oa6jmdMIvsYxGy+Nz8eQMTGgG1Z/O9kxX9E1xQ5R...` |

> Kunci jawaban dalam format encrypted/encoded

---

## PII Classification

| Severity | Count | Types |
|----------|-------|-------|
| **CRITICAL** | 1 | Plaintext password (DataPengawas) |
| **HIGH** | 130 | Email guru (66), Username/nama (64) |
| **MEDIUM** | 15 | Phone/ID patterns |
| **Total** | **146** | — |

---

*DataLeak Scanner · tools/dataleak.py · XC Hacking Hub · 2026-07-22*