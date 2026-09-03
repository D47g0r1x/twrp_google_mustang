#!/usr/bin/env python3
import sys
import struct
import os

def inspect_image(path):
    if not os.path.exists(path):
        print("File not found: " + path)
        return

    with open(path, "rb") as f:
        data = f.read(4096)
        magic = data[:4]
        if magic != b"AVB0":
            f.seek(0, 2)
            file_len = f.tell()
            if file_len > 64:
                f.seek(max(0, file_len - 4096))
                footer_data = f.read()
                idx = footer_data.find(b"AVB0")
                if idx != -1:
                    print("=== " + os.path.basename(path) + " (Embedded AVB footer found) ===")
                    return
            print("=== " + os.path.basename(path) + ": Not an AVB signed image or uses external vbmeta ===")
            return

        f.seek(0)
        hdr = f.read(256)
        v_maj, v_min = struct.unpack(">II", hdr[4:12])
        auth_sz, aux_sz = struct.unpack(">QQ", hdr[12:28])
        algo, hash_algo, rollback_idx, rollback_loc, flags = struct.unpack(">IIIII", hdr[28:48])
        release_str = hdr[48:96].split(b"\x00")[0].decode("utf-8", errors="ignore")

        algo_names = {
            0: "NONE", 1: "SHA256_RSA2048", 2: "SHA256_RSA4096",
            3: "SHA256_RSA8192", 4: "SHA512_RSA2048", 5: "SHA512_RSA4096"
        }
        algo_display = algo_names.get(algo, "Unknown (" + str(algo) + ")")

        print("=" * 60)
        print("AVB Metadata: " + os.path.basename(path))
        print("=" * 60)
        print("  AVB Version          : " + str(v_maj) + "." + str(v_min))
        print("  Algorithm            : " + algo_display)
        print("  Rollback Index       : " + str(rollback_idx))
        print("  Rollback Location    : " + str(rollback_loc))
        verif_state = "Disabled" if (flags & 1) else "Enabled"
        print("  AVB Flags            : " + hex(flags) + " (Verification " + verif_state + ")")
        if release_str:
            print("  Release Info         : " + release_str)

        f.seek(256 + auth_sz)
        aux = f.read(aux_sz)
        pos = 0
        props = []
        hashes = []
        chains = []
        while pos < len(aux):
            if pos + 16 > len(aux): break
            tag, num_bytes = struct.unpack(">QQ", aux[pos:pos+16])
            desc_bytes = aux[pos:pos+16+num_bytes]
            if tag == 0:
                k_len, v_len = struct.unpack(">QQ", desc_bytes[16:32])
                k = desc_bytes[32:32+k_len].decode("utf-8", errors="ignore")
                v = desc_bytes[32+k_len:32+k_len+v_len].decode("utf-8", errors="ignore")
                props.append((k, v))
            elif tag == 1:
                p_len = struct.unpack(">I", desc_bytes[44:48])[0]
                part_name = desc_bytes[88:88+p_len].decode("utf-8", errors="ignore")
                hashes.append(part_name)
            elif tag == 3:
                loc, key_len, name_len = struct.unpack(">IIQ", desc_bytes[16:32])
                name = desc_bytes[32:32+name_len].decode("utf-8", errors="ignore")
                chains.append((name, loc))
            pos += 16 + num_bytes

        if hashes:
            print("  Protected Partitions : " + ", ".join(hashes))
        if chains:
            print("  Chained Partitions   : " + ", ".join([f"{n} (loc {l})" for n, l in chains]))
        if props:
            print("  Build Properties     :")
            for k, v in props:
                clean_v = v.strip("\x00")
                if clean_v:
                    print("    - " + k + " = " + clean_v)

def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["vbmeta.img", "vbmeta_system.img", "vbmeta_vendor.img"]
    for t in targets:
        inspect_image(t)

if __name__ == "__main__":
    main()
