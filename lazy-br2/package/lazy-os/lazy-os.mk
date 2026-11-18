################################################################################
#
# lazy-os
#
################################################################################

LAZY_OS_VERSION = 3.0.0
LAZY_OS_SITE = $(BR2_EXTERNAL_LAZY_OS_PATH)/..
LAZY_OS_SITE_METHOD = local
LAZY_OS_DEPENDENCIES = python3 python-pyyaml

define LAZY_OS_INSTALL_TARGET_CMDS
	PY_LIB_DIR=`ls -d $(TARGET_DIR)/usr/lib/python3* 2>/dev/null | tail -n 1`; \
	mkdir -p "$$PY_LIB_DIR/site-packages/lazy"; \
	cp -r $(@D)/src/lazy/* "$$PY_LIB_DIR/site-packages/lazy/"

	mkdir -p $(TARGET_DIR)/usr/share/lazy/hud
	cp -r $(@D)/hud/* $(TARGET_DIR)/usr/share/lazy/hud/

	mkdir -p $(TARGET_DIR)/etc/lazy/capabilities
	cp -r $(@D)/config/capabilities/* $(TARGET_DIR)/etc/lazy/capabilities/

	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	cp -r $(@D)/systemd/*.service $(TARGET_DIR)/etc/systemd/system/ 2>/dev/null || true
	ln -sf /etc/systemd/system/lazy-gateway.service $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/lazy-gateway.service 2>/dev/null || true

	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 $(@D)/build/v2/lazy-os-rootfs/usr/bin/lazy-guest-daemon.py $(TARGET_DIR)/usr/bin/lazy-guest-daemon
endef

$(eval $(generic-package))
