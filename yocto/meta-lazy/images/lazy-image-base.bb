SUMMARY = "Lazy OS Base Minimal Image"
DESCRIPTION = "Minimal headless distribution profile used for OS evaluation and 40% size comparison."
LICENSE = "MIT"

inherit core-image

IMAGE_FEATURES += "ssh-server-openssh"

IMAGE_INSTALL = "\
    packagegroup-core-boot \
    systemd \
    systemd-extra-utils \
    btrfs-tools \
    python3-core \
    python3-json \
    python3-modules \
    python3-pyyaml \
    lazy-core \
"

IMAGE_LINGUAS = " "
