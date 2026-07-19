# One Tap Drag — FF Config Guide

> **Goal:** Aim nempel ke kepala saat shoot & drag — headshot rate maksimal

---

## Sensitivity Settings (Manual Input ke FF)

| Setting | Value | Kenapa |
|---------|-------|--------|
| General | **100** | Flick cepat, drag responsif |
| Red Dot | **85** | Balance antara speed & kontrol |
| 2x Scope | **72** | Tracking smooth saat spray |
| 4x Scope | **58** | Anti overshoot jarak medium |
| AWM Scope | **42** | Presisi jarak jauh |
| Free Look | **95** | Rotasi cepat lihat sekitar |

### Gyroscope (kalau pakai)
| Setting | Value |
|---------|-------|
| General | 80 |
| Red Dot | 70 |
| 2x | 60 |
| 4x | 45 |
| AWM | 30 |

---

## Teknik One Tap Headshot

```
1. Aim ke arah DADA musuh (bukan kepala)
2. TAP fire button
3. Saat BULLET PERTAMA keluar → drag aim ke ATAS (ke kepala)
4. Bullet kedua = HEADSHOT
```

**Key insight:** Aim ke dada dulu karena hitbox kepala kecil, drag dari bawah ke atas lebih akurat daripada aim langsung ke kepala

**Timing:** 80-100ms swipe dari dada → kepala

---

## Teknik Drag Headshot (Spray)

```
1. TAHAN fire button (jangan lepas)
2. Mulai aim di BADAN (chest/stomach)
3. Saat 2-3 bullet pertama keluar → DRAG UP secara diagonal
4. Compensate recoil dengan drag berlawanan arah pattern
```

**Best guns untuk drag:**
- `MP40` — fast fire rate, drag pendek
- `M1887` — 2 shot, drag 1x cukup
- `AK` — high damage, drag medium
- `M4A1` — low recoil, drag mudah

---

## Graphics Performance Setup

Masuk **FF → Settings → Graphics:**

| Setting | Value |
|---------|-------|
| Resolution | HD |
| Frame Rate | Ultra (60fps) |
| Graphics Quality | **Smooth** |
| Shadows | **OFF** |
| Auto Adjust | **OFF** |
| Bloom | **OFF** |

> **Kenapa Smooth?** FPS stabil 60 >>> grafis bagus tapi frame drop. Saat drag headshot, frame drop = miss!

---

## HUD Layout Rekomendasi

- **Fire button:** Besar (130), pojok kanan bawah, opacity 80%
- **Aim/scope:** Medium (100), kiri tengah
- **Crouch:** Kecil (80), kanan tengah
- **Joystick:** Besar (140), kiri bawah
- **Reload:** Kiri atas, kecil

> **Tip:** Fire button besar = hitarea lebih besar = gak meleset saat drag cepat

---

## Custom Room Test Protocol

1. Buka custom room dengan teman
2. Test **one tap** dari jarak 10m, 20m, 30m
3. Test **drag headshot** sambil jalan & diam
4. Kalau 70%+ headshot → sensitivity udah pas
5. Kalau overshoot (kena atas kepala) → turunin General 5 poin
6. Kalau undershoot (kena dada terus) → naikkan General 5 poin

---

## Apply via ADB (opsional, butuh USB Debugging)

```bash
chmod +x apply.sh
./apply.sh
```

Ini apply performance settings (animasi, cache clear, RAM boost).
Sensitivity tetap harus diinput manual di FF karena game protect nilai ini.
