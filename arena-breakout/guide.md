# Arena Breakout — XC MOD GUIDE

## Path Config (Target Folder)
```
/sdcard/Android/data/com.proximabeta.mf.u/files/UE4Game/MaoXian/MaoXian/Saved/Config/Android/
```

## Cara Apply (Pilih Salah Satu)

### Metode 1 — ADB (Paling Clean)
```bash
# Pastikan USB Debugging ON
bash apply.sh
```

### Metode 2 — MT Manager / ZArchiver (No PC)
1. Buka MT Manager / ZArchiver
2. Navigate ke path di atas
3. Copy `Engine.ini` dan `GameUserSettings.ini` ke folder itu
4. Overwrite kalau ada file lama
5. Restart game

### Metode 3 — Root File Manager
```
/data/data/com.proximabeta.mf.u/files/UE4Game/...
```
Path internal (butuh root), lebih permanen dari path sdcard.

---

## Apa yang Di-mod

### FPS Boost
- `r.Shadow.CSM.MaxCascades=0` — matiin shadow sepenuhnya (+15-20 fps)
- `r.BloomQuality=0` + `r.MotionBlurQuality=0` — matiin post-process berat
- `r.MobileContentScaleFactor=0.85` — render di 85% resolusi, upscale ke native
- `r.VSync=0` — lepas vsync lock
- `FrameRateLimit=120` — unlock sampai 120fps (device dependent)
- Threading parallel diaktifkan — CPU lebih efisien

### Visibility / Musuh Lebih Jelas
- Shadow off = musuh tidak tersembunyi shadow
- `r.LODFadeTime=0` — model musuh pop-in instan tanpa fade
- `TextureQuality=2` — texture tetap medium agar musuh visible jelas
- `ViewDistanceQuality=2` — jarak render musuh tetap jauh

### Network Smooth
- `NetClientTicksPerSecond=120` — tick rate client lebih tinggi
- `AsyncLoadingThreadEnabled=True` — load asset tidak block main thread
- `PktLag=0` semua — matiin packet simulation

---

## Note Penting
- File ini di-overwrite game setiap update. Re-apply setelah patch.
- Kalau game crash: hapus Engine.ini dulu, coba hanya GameUserSettings.ini.
- `r.MobileContentScaleFactor` — turunin ke `0.75` kalau device mid-range.
- Recoil di Arena Breakout = server-side. Tidak bisa di-mod via config file.
  Kontrol recoil tetap via teknik + gyro.
