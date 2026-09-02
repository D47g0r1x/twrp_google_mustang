#!/usr/bin/env python3
import os
import sys
import struct
import argparse

class Ext4Reader:
    def __init__(self, img_path):
        self.f = open(img_path, "rb")
        self.f.seek(1024)
        sb = self.f.read(1024)
        s_magic = struct.unpack("<H", sb[56:58])[0]
        if s_magic != 0xef53:
            raise ValueError(f"Invalid ext4 magic: {hex(s_magic)}")
        s_log_block_size = struct.unpack("<I", sb[24:28])[0]
        self.block_size = 1024 << s_log_block_size
        self.inodes_per_group = struct.unpack("<I", sb[40:44])[0]
        self.inode_size = struct.unpack("<H", sb[88:90])[0]
        self.desc_size = struct.unpack("<H", sb[254:256])[0] or 32

    def get_inode(self, ino):
        group = (ino - 1) // self.inodes_per_group
        index = (ino - 1) % self.inodes_per_group
        desc_offset = self.block_size + group * self.desc_size
        self.f.seek(desc_offset)
        desc = self.f.read(self.desc_size)
        inode_table_block = struct.unpack("<I", desc[8:12])[0]
        inode_offset = inode_table_block * self.block_size + index * self.inode_size
        self.f.seek(inode_offset)
        return self.f.read(self.inode_size)

    def _read_extents(self, data_bytes, curr_depth):
        magic, entries, max_entries, depth = struct.unpack("<HHHH", data_bytes[:8])
        if magic != 0xf30a:
            raise ValueError(f"Invalid extent magic: {hex(magic)}")
        blocks = []
        if depth == 0:
            for i in range(entries):
                ext = data_bytes[12 + i*12 : 24 + i*12]
                ee_block, ee_len, ee_start_hi, ee_start_lo = struct.unpack("<IHHI", ext)
                blocks.append(((ee_start_hi << 32) | ee_start_lo, ee_len))
        else:
            for i in range(entries):
                idx = data_bytes[12 + i*12 : 24 + i*12]
                ei_block, ei_leaf_lo, ei_leaf_hi, _ = struct.unpack("<IIHH", idx)
                leaf_pblock = (ei_leaf_hi << 32) | ei_leaf_lo
                self.f.seek(leaf_pblock * self.block_size)
                leaf_data = self.f.read(self.block_size)
                blocks.extend(self._read_extents(leaf_data, depth - 1))
        return blocks

    def read_inode_data(self, inode_bytes):
        size_lo = struct.unpack("<I", inode_bytes[4:8])[0]
        size_hi = struct.unpack("<I", inode_bytes[108:112])[0]
        size = (size_hi << 32) | size_lo
        flags = struct.unpack("<I", inode_bytes[32:36])[0]
        
        mode = struct.unpack("<H", inode_bytes[:2])[0]
        if (mode & 0xF000) == 0xA000 and size <= 60 and not (flags & 0x80000):
            return inode_bytes[40:40+size]

        extent_hdr = inode_bytes[40:100]
        magic, entries, max_entries, depth = struct.unpack("<HHHH", extent_hdr[:8])
        blocks = self._read_extents(extent_hdr, depth)
        res = bytearray()
        for pblock, ee_len in blocks:
            self.f.seek(pblock * self.block_size)
            res.extend(self.f.read(ee_len * self.block_size))
        return bytes(res[:size])

    def parse_dir(self, dir_bytes):
        pos = 0
        entries = {}
        while pos < len(dir_bytes):
            if pos + 8 > len(dir_bytes): break
            inode, rec_len, name_len, file_type = struct.unpack("<IHBB", dir_bytes[pos:pos+8])
            if rec_len == 0: break
            name = dir_bytes[pos+8:pos+8+name_len].decode("utf-8", errors="ignore")
            if inode != 0:
                entries[name] = (inode, file_type)
            pos += rec_len
        return entries

    def resolve_path(self, path):
        parts = [p for p in path.strip("/").split("/") if p]
        curr_ino = 2
        for i, part in enumerate(parts):
            inode_bytes = self.get_inode(curr_ino)
            mode = struct.unpack("<H", inode_bytes[:2])[0]
            if (mode & 0xF000) == 0xA000:
                target = self.read_inode_data(inode_bytes).decode("utf-8")
                rem = "/".join(parts[i:])
                return self.resolve_path(os.path.join(os.path.dirname("/" + "/".join(parts[:i])), target, rem))
            dir_data = self.read_inode_data(inode_bytes)
            entries = self.parse_dir(dir_data)
            if part not in entries:
                return None, None
            curr_ino, ftype = entries[part]
        return curr_ino, self.get_inode(curr_ino)

    def extract_file(self, rel_path, out_path):
        clean_path = rel_path.replace("vendor/", "", 1) if rel_path.startswith("vendor/") else rel_path
        ino, inode_b = self.resolve_path(clean_path)
        if not ino:
            return False, f"Not found in vendor.img: {rel_path}"
        data = self.read_inode_data(inode_b)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as out_f:
            out_f.write(data)
        mode = struct.unpack("<H", inode_b[:2])[0]
        os.chmod(out_path, mode & 0o777)
        return True, len(data)

    def close(self):
        self.f.close()

def main():
    parser = argparse.ArgumentParser(description="Extract proprietary blobs from vendor.img")
    parser.add_argument("-i", "--image", default="vendor.img", help="Path to vendor.img")
    parser.add_argument("-l", "--list", default="device/google/mustang/proprietary-files.txt", help="List of files to extract")
    parser.add_argument("-o", "--output", default="vendor/google/mustang", help="Output vendor tree path")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: {args.image} not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.list):
        print(f"Error: {args.list} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Opening {args.image}...")
    reader = Ext4Reader(args.image)
    
    extracted_files = []
    with open(args.list, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"Extracting {len(lines)} files to {args.output}...")
    prop_dir = os.path.join(args.output, "proprietary")
    for file_rel in lines:
        out_dest = os.path.join(prop_dir, file_rel)
        success, info = reader.extract_file(file_rel, out_dest)
        if success:
            extracted_files.append(file_rel)
            print(f"  [OK] {file_rel} ({info} bytes)")
        else:
            print(f"  [FAIL] {file_rel} - {info}")

    reader.close()

    # Generate vendor makefile: mustang-vendor.mk
    vendor_mk_path = os.path.join(args.output, "mustang-vendor.mk")
    lines_mk = [
        "# Automatically generated by extract-files.py",
        "# Do not edit manually",
        "",
        "PRODUCT_COPY_FILES += \\"
    ]
    for i, fpath in enumerate(extracted_files):
        sep = " \\" if i < len(extracted_files) - 1 else ""
        lines_mk.append(f"    vendor/google/mustang/proprietary/{fpath}:$(TARGET_COPY_OUT_RECOVERY)/root/{fpath}{sep}")
    with open(vendor_mk_path, "w") as mk:
        mk.write("\n".join(lines_mk) + "\n")

    # Generate vendor Android.mk
    android_mk_path = os.path.join(args.output, "Android.mk")
    lines_amk = [
        "# Automatically generated by extract-files.py",
        "LOCAL_PATH := $(call my-dir)",
        "",
        "ifeq ($(TARGET_DEVICE),mustang)",
        "include $(call all-subdir-makefiles,$(LOCAL_PATH))",
        "endif",
        ""
    ]
    with open(android_mk_path, "w") as amk:
        amk.write("\n".join(lines_amk))

    print(f"\nExtraction complete! {len(extracted_files)}/{len(lines)} files extracted.")
    print("Generated makefiles:")
    print(f"  - {vendor_mk_path}")
    print(f"  - {android_mk_path}")

if __name__ == "__main__":
    main()
