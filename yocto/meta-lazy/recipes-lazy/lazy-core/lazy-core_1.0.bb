SUMMARY = "Lazy OS Core Python Services, Manifests, HUD, and Systemd Units"
DESCRIPTION = "Core runtime services for Lazy OS (gateway, planner, policy, tasks, brokers, audit, outbox, routines)."
HOMEPAGE = "https://github.com/lazy-os/lazy-os"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit systemd useradd

RDEPENDS:${PN} += " \
    python3-core \
    python3-json \
    python3-modules \
    python3-pyyaml \
    btrfs-progs \
    util-linux \
"

USERADD_PACKAGES = "${PN}"
USERADD_PARAM:${PN} = " \
    --system --no-create-home --shell /bin/false --user-group lazy-gw; \
    --system --no-create-home --shell /bin/false --user-group lazy-plan; \
    --system --no-create-home --shell /bin/false --user-group lazy-llm; \
    --system --no-create-home --shell /bin/false --user-group lazy-pol; \
    --system --no-create-home --shell /bin/false --user-group lazy-task; \
    --system --no-create-home --shell /bin/false --user-group lazy-brk-fs; \
    --system --no-create-home --shell /bin/false --user-group lazy-brk-sys; \
    --system --no-create-home --shell /bin/false --user-group lazy-brk-hw; \
    --system --no-create-home --shell /bin/false --user-group lazy-brk-web; \
    --system --no-create-home --shell /bin/false --user-group lazy-brk-comms; \
    --system --no-create-home --shell /bin/false --user-group lazy-secrets; \
    --system --no-create-home --shell /bin/false --user-group lazy-outbox; \
    --system --no-create-home --shell /bin/false --user-group lazy-fetch; \
    --system --no-create-home --shell /bin/false --user-group lazy-rout; \
    --system --no-create-home --shell /bin/false --user-group lazy-audit; \
    --system --no-create-home --shell /bin/false --user-group lazy-sandbox \
"

SYSTEMD_SERVICE:${PN} = " \
    lazy-gateway.service \
    lazy-planner.service \
    lazy-llm.service \
    lazy-policy.service \
    lazy-tasks.service \
    lazy-broker-fs.service \
    lazy-broker-sys.service \
    lazy-broker-hw.service \
    lazy-broker-web.service \
    lazy-broker-comms.service \
    lazy-secrets.service \
    lazy-outbox.service \
    lazy-fetcher.service \
    lazy-routines.service \
    lazy-audit.service \
"
SYSTEMD_AUTO_ENABLE = "enable"

FILES:${PN} += " \
    ${libdir}/python3*/dist-packages/lazy \
    ${sysconfdir}/lazy \
    ${datadir}/lazy/hud \
    ${systemd_unitdir}/system \
    /var/lib/lazy \
"
