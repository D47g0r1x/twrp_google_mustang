# TWRP for Google Pixel 10 Pro XL (`mustang`) — Official Wiki & Technical Guide

Welcome to the technical wiki for the Google Pixel 10 Pro XL TWRP port. This document covers the hardware architecture, the internals of our File-Based Encryption (FBE) implementation, step-by-step flashing workflows, and debugging procedures for beta testers.

---

## 1. Beta Testing Disclaimer

```text
This release is labeled BETA.
While daily recovery tasks (partitions wipe, sideload, backups, and fastbootd)
have been verified, hardware-backed Titan M2 Phase 2 decryption on Android 16/17
is actively being tested. Keep an off-device backup of all important files!
```

---

## 2. Partition Architecture & GKI Layout

The Pixel 10 Pro XL uses Google's GKI (Generic Kernel Image) architecture with **Boot Header v4**. 

Unlike older Android devices, **there is no dedicated physical recovery partition**. Instead:
- The Linux kernel lives in `boot` (`boot_a` / `boot_b`).
- The initial boot ramdisk is in `init_boot`.
- **The recovery ramdisk is housed entirely inside `vendor_boot`** (`vendor_boot_a` / `vendor_boot_b`).

### Block Storage Mapping (`3c400000.ufs`)
- **Bootloader**: UFS 4.x controller mounted at `/dev/block/platform/3c400000.ufs/by-name/`
- **Dynamic Super Partition**: Logical volumes managed by Device Mapper (`system`, `system_dlkm`, `system_ext`, `product`, `vendor`, `vendor_dlkm`).
- **Metadata**: F2FS filesystem holding metadata encryption keys (`/dev/block/platform/3c400000.ufs/by-name/metadata`).
- **Userdata**: F2FS formatted volume encrypted with `aes-256-xts:aes-256-hctr2`.

---

## 3. How Titan M2 Hardware Decryption Works

Understanding how TWRP interacts with Android's encryption helps clarify why Phase 2 decryption requires proprietary blobs.

```
       +---------------------------------------------+
       |             TWRP Recovery GUI               |
       |  Prompts User for PIN / Pattern / Password  |
       +----------------------+----------------------+
                              |
                              v
       +---------------------------------------------+
       |             vold / Cryptfs HW               |
       +----------------------+----------------------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
    +-------------------+           +-------------------+
    |    Citadel HAL    |           |    Trusty TEE     |
    |   (/dev/citadel)  |           | (/dev/trusty-ipc) |
    +---------+---------+           +---------+---------+
              |                               |
              v                               v
   +---------------------+         +---------------------+
   |   Google Titan M2   |         | KeyMint / Gatekeeper|
   | Hardware Token Gate |         |  Credential Unseal  |
   +---------------------+         +---------------------+
              \                               /
               \                             /
                v                           v
       +---------------------------------------------+
       |           Synthetic Password (SP)           |
       |  Decrypted Key Derives Filesystem Master Key|
       +----------------------+----------------------+
                              |
                              v
       +---------------------------------------------+
       |          /data Mounted Read/Write           |
       +---------------------------------------------+
```

### Phase 1: Device-Encrypted (DE) Storage
- Unlocked early during boot using a key derived from hardware tokens stored in `/metadata/vold/metadata_encryption`.
- Does not require the user's personal password or PIN.
- Allows TWRP to read basic device properties, logs, and system data.

### Phase 2: Credential-Encrypted (CE) Storage (Beta Focus)
- Stores personal apps, pictures, downloads, and user settings (`/data/user/0`).
- Protected by a **Synthetic Password (SP)**.
- To unseal the Synthetic Password, the user's PIN/pattern must be authenticated against the **Weaver HAL** on the **Titan M2 security chip** and verified by **Gatekeeper** running in the Trusty secure world.
- If the Citadel daemon (`citadeld`) or the KeyMint/Weaver HALs cannot establish IPC with `/dev/citadel`, the device cannot derive the master key, and `/data` remains encrypted.

---

## 4. Flashing & Testing Guide

### Prerequisites
1. **Unlock the bootloader**:
   - Enable *Developer Options* > *OEM Unlocking* in Android settings.
   - Reboot to fastboot: `adb reboot bootloader`
   - Run: `fastboot flashing unlock` and confirm on the phone screen.
2. **Download Platform Tools**: Ensure you have the latest `fastboot` binary from Google.

### Testing Without Overwriting Your Active Slot (Recommended)
You can test this recovery safely using the inactive slot trick without touching your working Android slot:

```bash
# 1. Identify your active slot
fastboot getvar current-slot
# Example output: current-slot: a

# 2. Flash TWRP only to the opposite slot (e.g. b)
fastboot flash vendor_boot_b vendor_boot.img

# 3. Switch to slot b to test
fastboot --set-active=b

# 4. Reboot directly into recovery
fastboot reboot recovery
```

If you ever want to return back to stock immediately:
```bash
fastboot --set-active=a
fastboot reboot
```

### Flashing Permanently
Once tested:
```bash
fastboot flash vendor_boot_a vendor_boot.img
fastboot flash vendor_boot_b vendor_boot.img
fastboot reboot recovery
```

---

## 5. Troubleshooting & Frequently Asked Questions

### Q: TWRP asks for a password, but I only have a PIN/Pattern set.
- **Pattern**: If using a 3x3 pattern, enter the dots as numbers from `1` to `9` (top-left is 1, bottom-right is 9).
- **PIN**: Use the standard numeric keypad.

### Q: Decryption reports "Failed to decrypt data" or hangs.
Because this is a Beta build, the Weaver slot negotiation may need calibration for your specific OS patch level.
1. Leave the phone plugged into your computer.
2. Run:
   ```bash
   adb pull /tmp/recovery.log
   adb logcat -d | grep -iE "citadel|keymint|weaver|gatekeeper" > citadel_debug.log
   ```
3. Share the log on the GitHub Issues page so we can adjust the service init timing.

### Q: Touchscreen is unresponsive in recovery.
- If the touch driver initializes late on cold boot, press the power button twice to toggle the display off and back on.
- Alternatively, plug in a USB mouse via an OTG adapter; TWRP supports standard USB HID pointer input.

### Q: How do I revert to the 100% stock recovery?
Simply extract `vendor_boot.img` from the official factory image or OTA file for your device build, and reflash it:
```bash
fastboot flash vendor_boot stock_vendor_boot.img
```

---

## 6. Filing Useful Bug Reports

When opening an issue, please include:
1. **Device exact model** (e.g., Pixel 10 Pro XL).
2. **Stock OS build number** (e.g., `CP2A.260805.005`).
3. **Lockscreen security type** (PIN, Pattern, alphanumeric password, or none).
4. **Attached logs**:
   - `/tmp/recovery.log`
   - `adb logcat` output during the decryption attempt.
