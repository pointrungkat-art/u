#!/bin/bash
# One Tap Drag — FF Config Auto-Apply via ADB
# Requirement: ADB enabled (USB Debugging ON) + PC/Mac connected ke device
# Atau jalanin di Android via Termux dengan ADB wireless

FF_PKG="com.dts.freefireth"
FF_MAX_PKG="com.dts.freefiremaxob"
ADB="adb"

BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║   One Tap Drag — FF Config Applier   ║"
echo "║   v1.0 | XC Hub Project              ║"
echo "╚══════════════════════════════════════╝"
echo -e "${RESET}"

# Cek ADB tersedia
if ! command -v adb &> /dev/null; then
    echo -e "${RED}[ERROR] ADB tidak ditemukan. Install ADB dulu!${RESET}"
    echo "  → https://developer.android.com/studio/releases/platform-tools"
    exit 1
fi

# Cek device terconnect
DEVICE=$($ADB devices | grep -v "List of devices" | grep "device$" | awk '{print $1}' | head -1)
if [ -z "$DEVICE" ]; then
    echo -e "${RED}[ERROR] Tidak ada device terdeteksi!${RESET}"
    echo "  1. Aktifkan USB Debugging di Settings → Developer Options"
    echo "  2. Colok kabel USB"
    echo "  3. Allow USB Debugging di popup HP"
    exit 1
fi

echo -e "${GREEN}[OK] Device: ${DEVICE}${RESET}"

# Deteksi versi FF yang terinstall
FF_INSTALLED=$($ADB -s "$DEVICE" shell pm list packages | grep "$FF_PKG" | head -1)
if echo "$FF_INSTALLED" | grep -q "$FF_MAX_PKG"; then
    ACTIVE_PKG="$FF_MAX_PKG"
    echo -e "${CYAN}[INFO] Free Fire MAX terdeteksi${RESET}"
elif echo "$FF_INSTALLED" | grep -q "$FF_PKG"; then
    ACTIVE_PKG="$FF_PKG"
    echo -e "${CYAN}[INFO] Free Fire terdeteksi${RESET}"
else
    echo -e "${RED}[ERROR] Free Fire tidak terinstall!${RESET}"
    exit 1
fi

FF_DATA="/sdcard/Android/data/${ACTIVE_PKG}/files"

# Backup config lama
echo -e "\n${YELLOW}[1/4] Backup config lama...${RESET}"
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
$ADB -s "$DEVICE" pull "$FF_DATA/Sensitive" "$BACKUP_DIR/" 2>/dev/null
$ADB -s "$DEVICE" pull "$FF_DATA/GameSetting" "$BACKUP_DIR/" 2>/dev/null
echo -e "${GREEN}      Backup saved → ${BACKUP_DIR}${RESET}"

# Apply sensitivity settings via am broadcast
echo -e "\n${YELLOW}[2/4] Apply sensitivity settings...${RESET}"
$ADB -s "$DEVICE" shell settings put system pointer_speed 7
# General sensitivity via game data (FF baca dari file internal)
# Buat file sensitivity temp
cat > /tmp/ff_sens.txt << 'SENS'
SensitivityGeneral=100
SensitivityRedDot=85
SensitivityScope2x=72
SensitivityScope4x=58
SensitivityScopeAWM=42
SensitivityFreeLook=95
SensitivityGyroGeneral=80
SensitivityGyroRedDot=70
SensitivityGyroScope2x=60
SensitivityGyroScope4x=45
SensitivityGyroScopeAWM=30
SENS
$ADB -s "$DEVICE" push /tmp/ff_sens.txt "$FF_DATA/ff_onetap_config.txt" 2>/dev/null
echo -e "${GREEN}      Sensitivity config pushed${RESET}"

# Apply graphics performance settings
echo -e "\n${YELLOW}[3/4] Apply performance graphics...${RESET}"
$ADB -s "$DEVICE" shell settings put system animator_duration_scale 0.5
$ADB -s "$DEVICE" shell settings put global window_animation_scale 0.5
$ADB -s "$DEVICE" shell settings put global transition_animation_scale 0.5
# Kill background apps untuk max RAM
$ADB -s "$DEVICE" shell am kill-all
echo -e "${GREEN}      Performance mode aktif${RESET}"

# Clear FF cache
echo -e "\n${YELLOW}[4/4] Clear FF cache...${RESET}"
$ADB -s "$DEVICE" shell pm clear-cache "$ACTIVE_PKG" 2>/dev/null || true
echo -e "${GREEN}      Cache cleared${RESET}"

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════╗"
echo "║        DONE! Config Applied!         ║"
echo "╚══════════════════════════════════════╝${RESET}"
echo ""
echo -e "${CYAN}Langkah selanjutnya:${RESET}"
echo "  1. Buka FF → Settings → Sensitivity"
echo "  2. Set manual sesuai config.json (karena FF proteksi direct write)"
echo "  3. Masuk custom room → test one tap drag"
echo ""
echo -e "${YELLOW}[TIP] Sensitivity terbaik buat one tap drag:${RESET}"
echo "  General: 100 | Red Dot: 85 | 2x: 72"
echo "  4x: 58  | AWM: 42  | Free Look: 95"
echo ""
