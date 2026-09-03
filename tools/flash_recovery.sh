#!/usr/bin/env bash
# Helper script to safely test or flash TWRP / OrangeFox on Pixel 10 Pro XL

set -e

IMAGE="${1:-vendor_boot.img}"

if [ ! -f "${IMAGE}" ]; then
    echo "Error: Image file '${IMAGE}' not found."
    echo "Usage: ./flash_recovery.sh [path_to_vendor_boot.img]"
    exit 1
fi

echo "=========================================================="
echo "Pixel 10 Pro XL (mustang) Fastboot Recovery Helper"
echo "Target Image: ${IMAGE}"
echo "=========================================================="

echo "[1/4] Checking fastboot devices..."
DEVICE=$(fastboot devices | awk '{print $1}')

if [ -z "${DEVICE}" ]; then
    echo "No fastboot device detected!"
    echo "Please connect your phone and enter fastboot mode: adb reboot bootloader"
    exit 1
fi

echo "Detected device: ${DEVICE}"

echo "[2/4] Detecting current active slot..."
CURRENT_SLOT=$(fastboot getvar current-slot 2>&1 | grep "current-slot:" | awk '{print $2}' | tr -d '\r')
echo "Active slot is: ${CURRENT_SLOT}"

if [ "${CURRENT_SLOT}" = "a" ]; then
    INACTIVE_SLOT="b"
else
    INACTIVE_SLOT="a"
fi

echo ""
echo "Select flashing mode:"
echo "  1) Safe Test Boot (flashes to inactive slot '${INACTIVE_SLOT}' and boots recovery)"
echo "  2) Permanent Flash (flashes to BOTH slots a and b)"
echo "  3) Cancel"
read -p "Enter choice [1-3]: " CHOICE

case "${CHOICE}" in
    1)
        echo "Flashing ${IMAGE} to vendor_boot_${INACTIVE_SLOT}..."
        fastboot flash "vendor_boot_${INACTIVE_SLOT}" "${IMAGE}"
        echo "Setting active slot to ${INACTIVE_SLOT}..."
        fastboot --set-active="${INACTIVE_SLOT}"
        echo "Rebooting into recovery..."
        fastboot reboot recovery
        echo "Done! If recovery has issues, switch back: fastboot --set-active=${CURRENT_SLOT}"
        ;;
    2)
        echo "Flashing ${IMAGE} to vendor_boot_a..."
        fastboot flash vendor_boot_a "${IMAGE}"
        echo "Flashing ${IMAGE} to vendor_boot_b..."
        fastboot flash vendor_boot_b "${IMAGE}"
        echo "Rebooting into recovery..."
        fastboot reboot recovery
        echo "Done! Recovery permanently updated on both slots."
        ;;
    *)
        echo "Aborted."
        exit 0
        ;;
esac
