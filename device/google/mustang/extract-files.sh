#!/usr/bin/env bash
# Wrapper to extract proprietary files for Pixel 10 Pro XL (mustang)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

VENDOR_IMG="${1:-${ROOT_DIR}/vendor.img}"
PROPRIETARY_LIST="${SCRIPT_DIR}/proprietary-files.txt"
OUTPUT_DIR="${ROOT_DIR}/vendor/google/mustang"

python3 "${SCRIPT_DIR}/extract-files.py" \
    --image "${VENDOR_IMG}" \
    --list "${PROPRIETARY_LIST}" \
    --output "${OUTPUT_DIR}"
