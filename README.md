# TeamWin Recovery Project (TWRP) for Google Pixel 10 Pro XL (`mustang`)

```text
/*
 * Your warranty is now void.
 *
 * We are not responsible for bricked devices, dead storage chips, thermonuclear war,
 * or your alarm failing because the phone stayed in recovery loop.
 * YOU are choosing to make these modifications. Please backup your data first!
 */
```

Welcome to the custom TWRP recovery project for the **Google Pixel 10 Pro XL** (codename: `mustang`), powered by the **Google Tensor G5** (`laguna`) SoC running **Android 16 / 17**.

> ⚠️ **IMPORTANT BETA NOTICE**  
> This is an **early experimental Beta build**. While standard recovery operations (wiping, formatting, flashing zips, adb/fastbootd, and USB-OTG) are functional, **Phase 2 hardware-backed decryption (Weaver/Titan M2 user PIN/pattern/password unlock)** is under active testing on Tensor G5 hardware. Always keep a full backup of your device before testing!

---

## Device Specs & Platform Info

| Attribute | Details |
| :--- | :--- |
| **Device Model** | Google Pixel 10 Pro XL |
| **Codename** | `mustang` |
| **Platform / SoC** | Google Tensor G5 (`laguna`) |
| **Architecture** | ARM64 (`armv8-a` / `armv9-a` cores, 64-bit only) |
| **Kernel / Architecture** | GKI (Generic Kernel Image) with Boot Header v4 |
| **Recovery Location** | Dedicated `vendor_boot` partition (`3c400000.ufs`) |
| **Stock Firmware Base** | Android 17 (`CP2A.260805.005`, August 2026 patch level) |
| **Security Module** | Google Titan M2 via Citadel HAL (`/dev/citadel`) & Trusty TEE |

---

## Current Status (Beta)

!!!!! CP2A.260805.005 !!!!!
!!!!!  ONLY FOR NOW.  !!!!!

- [x] **Touch & Display**: Working (native 1344x2992 resolution scaled to portrait HDPI theme).
- [x] **ADB & Fastbootd**: Working over USB controller (`c400000.dwc3`).
- [x] **External Storage**: USB-OTG drives (FAT32/exFAT/NTFS) mount properly.
- [x] **Partitions**: Full dynamic partition recognition (`system`, `system_dlkm`, `system_ext`, `product`, `vendor`, `vendor_dlkm`).
- [x] **Phase 1 Decryption (DE)**: Metadata decryption mounted via `/metadata/vold/metadata_encryption`.
- [x] **Titan M2 Daemons**: Citadel daemon (`citadeld`), KeyMint (`android.hardware.security.keymint-service.citadel`), and Weaver HAL bundled in recovery ramdisk.
- [/] **Phase 2 Decryption (CE)**: **[Testing in Beta]** Hardware PIN/Pattern unlock of user storage (`/data`). Please report test results with logs!

---

## Quick Start: How to Boot or Flash

Because modern Pixels use GKI architecture with Boot Header v4, recovery is packaged inside `vendor_boot.img` rather than a separate recovery partition.

### 1. Requirements
- An **unlocked bootloader** (`fastboot flashing unlock`).
- Up-to-date Google Platform Tools (`adb` and `fastboot`).
- Downloaded `vendor_boot.img` from the GitHub Releases or Actions Artifacts tab.

### 2. Testing First (Recommended)
Before replacing your stock recovery, try live-booting or flashing to your secondary inactive slot:

```bash
# Reboot into fastboot mode
adb reboot bootloader

# Option A: Direct temporary boot (if supported by bootloader)
fastboot boot vendor_boot.img

# Option B: Safe dual-slot test (flashes only to inactive slot B)
fastboot flash vendor_boot_b vendor_boot.img
fastboot --set-active=b
fastboot reboot
```

### 3. Permanent Installation
Once satisfied with the test boot:
```bash
# Flash to both slots
fastboot flash vendor_boot_a vendor_boot.img
fastboot flash vendor_boot_b vendor_boot.img
fastboot reboot recovery
```

---

## How to Test Decryption & Report Bugs

If you run into issues, especially with screen unlock or decryption, logs are essential to help us refine the proprietary Citadel/Weaver interfaces:

1. Connect your phone to your computer via USB while in TWRP.
2. Pull the recovery log:
   ```bash
   adb pull /tmp/recovery.log recovery_debug.log
   ```
3. Capture the security and HAL logs:
   ```bash
   adb logcat -d | grep -iE "citadel|keymint|weaver|gatekeeper|vold|fbe" > logcat_crypto.log
   ```
4. Open an Issue on this repository and attach both `.log` files along with:
   - Your exact Android OS build number
   - Whether you have a lockscreen PIN, pattern, or password set

---

## Building from Source

This tree is configured to build against the official minimal TWRP manifest (`twrp-12.1`):

```bash
# 1. Initialize manifest
mkdir -p twrp && cd twrp
repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags

# 2. Clone device and vendor trees
git clone https://github.com/D47g0r1x/twrp_google_mustang.git local_repo
mkdir -p device/google/mustang vendor/google/mustang
cp -r local_repo/device/google/mustang/* device/google/mustang/
cp -r local_repo/vendor/google/mustang/* vendor/google/mustang/

# 3. Compile
export ALLOW_MISSING_DEPENDENCIES=true
source build/envsetup.sh
lunch twrp_mustang-eng
mka vendorbootimage -j$(nproc --all)
```

---

## Credits & Acknowledgements
- **TeamWin Recovery Project** for the recovery framework.
- **The minimal-manifest-twrp maintainers** for the lightweight build environment.
- **Google** for AOSP, Tensor G5 platform files, and kernel sources.
- The open-source Android modding community for ongoing reverse engineering of modern Titan M2 / Trusty FBE decryption.
