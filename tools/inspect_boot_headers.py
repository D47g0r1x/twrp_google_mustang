#!/usr/bin/env python3
"""
Inspect Android Boot Header v3/v4 & Vendor Boot Header v4
For Pixel 10 Pro XL (mustang / laguna)
"""

import sys
import struct
import os

def inspect_boot_image(path):
    if not os.path.exists(path):
        return
    with open(path, "rb") as f:
        magic = f.read(8)
        f.seek(0)
        hdr = f.read(2128)
        print("=" * 60)
        print(f"File: {os.path.basename(path)} ({os.path.getsize(path):,} bytes)")
        print("=" * 60)
        if magic.startswith(b"ANDROID!"):
            v = struct.unpack("<I", hdr[40:44])[0] if len(hdr) >= 44 else "Unknown"
            print(f"  Type              : Android Boot Image (Header v{v})")
            if v in (3, 4):
                k_size, r_size = struct.unpack("<II", hdr[8:16])
                os_version = struct.unpack("<I", hdr[16:20])[0]
                os_patch = os_version & 0x7FF
                os_yr = 2000 + (os_patch >> 4)
                os_mo = os_patch & 0xF
                print(f"  Kernel Size       : {k_size:,} bytes")
                print(f"  Ramdisk Size      : {r_size:,} bytes")
                print(f"  OS Patch Level    : {os_yr:04d}-{os_mo:02d}")
        elif magic.startswith(b"VNDRBOOT"):
            v = struct.unpack("<I", hdr[8:12])[0]
            page_size = struct.unpack("<I", hdr[12:16])[0]
            r_size = struct.unpack("<I", hdr[24:28])[0]
            dtb_size = struct.unpack("<I", hdr[2100:2104])[0] if len(hdr) >= 2104 else 0
            tbl_size, entry_num, entry_size, bootconfig_size = struct.unpack("<IIII", hdr[2112:2128]) if len(hdr) >= 2128 else (0,0,0,0)
            cmdline = hdr[28:28+2048].split(b"\x00")[0].decode("utf-8", errors="ignore")
            print(f"  Type              : Vendor Boot Image (Header v{v})")
            print(f"  Page Size         : {page_size}")
            print(f"  Vendor Ramdisk    : {r_size:,} bytes")
            print(f"  DTB Size          : {dtb_size:,} bytes")
            print(f"  Ramdisk Table     : {entry_num} entries ({tbl_size} bytes)")
            print(f"  Bootconfig Size   : {bootconfig_size} bytes")
            if cmdline:
                print(f"  Kernel Cmdline    : {cmdline}")

def main():
    images = sys.argv[1:] if len(sys.argv) > 1 else ["boot.img", "init_boot.img", "vendor_boot.img", "vendor_kernel_boot.img"]
    for img in images:
        inspect_boot_image(img)

if __name__ == "__main__":
    main()
