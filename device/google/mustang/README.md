# TWRP Device Tree for Google Pixel 10 Pro XL (mustang)

## Overview
This device tree enables building TWRP for the Google Pixel 10 Pro XL (`mustang`), based on the Google Tensor G5 (`laguna`) platform running Android 16/17 (Build ID `CP2A.260805.005`).

## Hardware & Firmware Specifications
- **Device**: Pixel 10 Pro XL (`mustang`)
- **Platform / SoC**: Google Tensor G5 (`laguna`)
- **Architecture**: ARM64 (`armv9-a`), 64-bit only
- **Boot Header Version**: 4 (`boot.img` GKI kernel + `vendor_boot.img` recovery ramdisk)
- **Kernel Page Size**: 2048 (supports 16KB kernel pages)
- **Boot Storage Controller**: `/dev/block/platform/3c400000.ufs`
- **USB Controller**: `c400000.dwc3`

## Partition Layout
- **Boot / Kernel**: `/dev/block/platform/3c400000.ufs/by-name/boot` (Slot-select A/B)
- **Init Ramdisk**: `/dev/block/platform/3c400000.ufs/by-name/init_boot`
- **Vendor Boot (Recovery Ramdisk)**: `/dev/block/platform/3c400000.ufs/by-name/vendor_boot`
- **Metadata**: `/dev/block/platform/3c400000.ufs/by-name/metadata` (F2FS)
- **Userdata**: `/dev/block/platform/3c400000.ufs/by-name/userdata` (F2FS, FBE encrypted)
- **Dynamic Partitions**: `system`, `system_dlkm`, `system_ext`, `product`, `vendor`, `vendor_dlkm`

## Titan M2 & Decryption Architecture
The device uses File-Based Encryption (FBE) with metadata encryption (`keydirectory=/metadata/vold/metadata_encryption`).

### Phase 1 (Device-Encrypted / DE Data)
- Handled via metadata encryption and hardware FBE key slots derived from early keystore / Keymint.

### Phase 2 (Credential-Encrypted / CE Data)
- Requires interaction with the Titan M2 hardware security module (`/dev/citadel`) and Trusty TEE (`/dev/trusty-ipc-dev0`).
- Daemons executed in recovery:
  - `citadeld`: Citadel daemon interfacing with the Titan M2 chip.
  - `android.hardware.security.keymint-service.citadel`: KeyMint HAL backed by Titan M2.
  - `android.hardware.weaver-service.citadel`: Weaver HAL storing password slot tokens.
  - `android.hardware.gatekeeper-service.trusty`: Gatekeeper HAL for password authentication.
  - `android.hardware.security.keymint-service.rust.trusty`: Trusty KeyMint fallback/support.

## How to Build
```bash
# Initialize minimal TWRP manifest (Android 14/15/16 branch)
repo init --depth=1 -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-14

# Sync sources
repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags

# Setup environment
source build/envsetup.sh
lunch twrp_mustang-eng

# Build vendor_boot recovery image
mka vendorbootimage -j$(nproc --all)
```
