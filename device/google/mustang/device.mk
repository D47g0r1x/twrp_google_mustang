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

# Enable project pathmap
$(call project-pathmap-or-honor,TARGET_DEVICE_DIR,device/google/mustang)

# Recovery fstab and flags
PRODUCT_COPY_FILES += \
    $(DEVICE_PATH)/recovery/root/system/etc/recovery.fstab:$(TARGET_COPY_OUT_RECOVERY)/root/system/etc/recovery.fstab \
    $(DEVICE_PATH)/recovery/root/system/etc/twrp.flags:$(TARGET_COPY_OUT_RECOVERY)/root/system/etc/twrp.flags

# Init scripts
PRODUCT_COPY_FILES += \
    $(DEVICE_PATH)/recovery/root/init.recovery.laguna.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.laguna.rc \
    $(DEVICE_PATH)/recovery/root/init.recovery.mustang.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.mustang.rc \
    $(DEVICE_PATH)/recovery/root/init.recovery.citadel.rc:$(TARGET_COPY_OUT_RECOVERY)/root/init.recovery.citadel.rc

# Recovery utilities
PRODUCT_PACKAGES += \
    fastbootd \
    resetprop
