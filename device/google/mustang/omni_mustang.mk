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

# Inherit from generic 64-bit config
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)

# Inherit from TWRP configuration (handles both twrp and omni vendors)
$(call inherit-product-if-exists, vendor/twrp/config/common.mk)
$(call inherit-product-if-exists, vendor/omni/config/common.mk)

# Inherit from device configuration
$(call inherit-product, device/google/mustang/device.mk)

# Inherit from extracted vendor proprietary blobs
$(call inherit-product-if-exists, vendor/google/mustang/mustang-vendor.mk)

PRODUCT_DEVICE := mustang
PRODUCT_NAME := omni_mustang
PRODUCT_BRAND := google
PRODUCT_MODEL := Pixel 10 Pro XL
PRODUCT_MANUFACTURER := Google

PRODUCT_GMS_CLIENTID_BASE := android-google

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRODUCT_NAME=mustang \
    TARGET_DEVICE=mustang \
    BUILD_FINGERPRINT="google/mustang/mustang:17/CP2A.260805.005/15828068:user/release-keys"
