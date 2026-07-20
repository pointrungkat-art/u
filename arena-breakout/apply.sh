#!/bin/bash
# Arena Breakout — XC File Injector
# Requires ADB + USB Debugging ON
# Atau copy manual via MT Manager / ZArchiver ke path di bawah

PACKAGE="com.proximabeta.mf.u"
CONFIG_PATH="/sdcard/Android/data/$PACKAGE/files/UE4Game/MaoXian/MaoXian/Saved/Config/Android"

echo "[XC] === Arena Breakout Config Injector ==="
echo "[XC] Target: $CONFIG_PATH"

# Pastikan folder ada
adb shell mkdir -p "$CONFIG_PATH"

# Push config files
echo "[XC] Injecting Engine.ini..."
adb push Engine.ini "$CONFIG_PATH/Engine.ini"

echo "[XC] Injecting GameUserSettings.ini..."
adb push GameUserSettings.ini "$CONFIG_PATH/GameUserSettings.ini"

# Set permission biar ke-read
adb shell chmod 644 "$CONFIG_PATH/Engine.ini"
adb shell chmod 644 "$CONFIG_PATH/GameUserSettings.ini"

# CPU Performance mode via ADB (tanpa root)
echo "[XC] Setting CPU performance mode..."
adb shell settings put global animator_duration_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global window_animation_scale 0

# Clear game cache biar settings langsung apply
echo "[XC] Clearing game cache..."
adb shell pm clear --cache-only $PACKAGE 2>/dev/null || true

echo ""
echo "[XC] DONE — buka Arena Breakout sekarang"
echo "[XC] Settings override aktif: FPS unlock + shadow off + no motion blur"
echo ""
echo "[ MANUAL PATH kalau no ADB ]"
echo "Copy Engine.ini + GameUserSettings.ini ke:"
echo "$CONFIG_PATH"
