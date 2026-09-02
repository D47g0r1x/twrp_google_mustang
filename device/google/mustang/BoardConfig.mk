#
# Copyright (C) 2026 The Android Open Source Project
# Copyright (C) 2026 TeamWin Recovery Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

DEVICE_PATH := device/google/mustang

# Architecture (Strictly 64-bit only on Tensor G5 / Laguna)
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv9-a
TARGET_CPU_ABI := arm64-v8a
TARGET_CPU_VARIANT := generic

TARGET_2ND_ARCH :=
TARGET_2ND_ARCH_VARIANT :=
TARGET_2ND_CPU_ABI :=
TARGET_2ND_CPU_VARIANT :=

# Platform
TARGET_BOARD_PLATFORM := laguna
TARGET_BOOTLOADER_BOARD_NAME := mustang
TARGET_USES_64_BIT_BINDER := true

# Boot / Vendor Boot Header v4
BOARD_BOOT_HEADER_VERSION := 4
BOARD_KERNEL_PAGESIZE := 2048
BOARD_RAMDISK_USE_LZ4 := true
BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT := true
BOARD_INCLUDE_RECOVERY_RAMDISK_IN_VENDOR_BOOT := true

# Kernel Parameters & Bootconfig from Stock Laguna Kernel
BOARD_BOOTCONFIG := \
    androidboot.load_modules_parallel=true \
    androidboot.boot_devices=3c400000.ufs

BOARD_KERNEL_CMDLINE := \
    fips140.load_sequential=1 \
    vh_sched.load_sequential=1 \
    spmi_smartdv.load_sequential=1 \
    regmap-goog-spmi.load_sequential=1 \
    max77779_pmic.load_sequential=1 \
    max77779_pmic_spmi.load_sequential=1 \
    max77779_pmic_pinctrl.load_sequential=1 \
    dyndbg="func alloc_contig_dump_pages +p" \
    cma_sysfs.experimental=Y \
    cgroup.memory=nokmem \
    init_on_alloc=0 \
    init_on_free=1 \
    rcupdate.rcu_expedited=1 \
    rcu_nocbs=all \
    rcutree.enable_rcu_lazy \
    swiotlb=noforce \
    disable_dma32=on \
    sysctl.kernel.sched_pelt_multiplier=4 \
    aoc_core.aoc_enable_gsa_boot=1 \
    rodata=on \
    arm_smmu_v3_kvm.smc_s2=true \
    kasan=off \
    at24.write_timeout=100 \
    log_buf_len=1024K \
    android_arch_task_struct_size=512 \
    androidboot.selinux=permissive

# Partition Sizes
BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864
BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 67108864

# Dynamic Partitions
BOARD_SUPER_PARTITION_GROUPS := google_dynamic_partitions
BOARD_GOOGLE_DYNAMIC_PARTITIONS_PARTITION_LIST := \
    system \
    system_dlkm \
    system_ext \
    product \
    vendor \
    vendor_dlkm

# Filesystem Support
TARGET_USERIMAGES_USE_EXT4 := true
TARGET_USERIMAGES_USE_F2FS := true
BOARD_USES_METADATA_PARTITION := true

# Display & GUI Configuration
TARGET_RECOVERY_PIXEL_FORMAT := RGBX_8888
TW_THEME := portrait_hdpi
TW_SCREEN_WIDTH := 1344
TW_SCREEN_HEIGHT := 2992
TW_STATUS_ICONS_ALIGN := center
TW_CUSTOM_CPU_TEMP_PATH := /sys/devices/virtual/thermal/thermal_zone0/temp
TW_BRIGHTNESS_PATH := /sys/class/backlight/panel0-backlight/brightness
TW_MAX_BRIGHTNESS := 4095
TW_DEFAULT_BRIGHTNESS := 1024

# Recovery / TWRP General Options
RECOVERY_SDCARD_ON_DATA := true
TW_NO_FASTBOOT_BOOT := true
TW_LOAD_VENDOR_BOOT_MODULES := true
TW_LOAD_VENDOR_MODULES := true
TW_USE_EXTERNAL_STORAGE_FOR_BACKUP := true
TW_PREPARE_DATA_MEDIA_EARLY := true
TW_EXCLUDE_DEFAULT_USB_INIT := true
TW_INCLUDE_LIBRESETPROP := true
TW_INCLUDE_REPACKTOOLS := true

# Encryption & Titan M2 Decryption Configuration
TW_INCLUDE_CRYPTO := true
TW_INCLUDE_CRYPTO_FBE := true
TW_INCLUDE_FBE_METADATA_DECRYPT := true

# System Property Overrides for FBE Key Derivation
TW_OVERRIDE_SYSTEM_PROPS := \
    "ro.build.version.sdk=37;ro.build.version.release=17"
