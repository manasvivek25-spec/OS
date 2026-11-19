################################################################################
#
# lazy-os
#
################################################################################

LAZY_OS_VERSION = 3.0.0
LAZY_OS_SITE = /home/manas/lazy-os-src
LAZY_OS_SITE_METHOD = local
LAZY_OS_DEPENDENCIES = python3 python-pyyaml python-jsonschema

define LAZY_OS_INSTALL_TARGET_CMDS
	PY_LIB_DIR=`ls -d $(TARGET_DIR)/usr/lib/python3* 2>/dev/null | tail -n 1`; \
	mkdir -p "$$PY_LIB_DIR/site-packages/lazy"; \
	cp -r $(@D)/src/lazy/* "$$PY_LIB_DIR/site-packages/lazy/"

	mkdir -p $(TARGET_DIR)/usr/share/lazy/hud
	cp -r $(@D)/hud/* $(TARGET_DIR)/usr/share/lazy/hud/

	mkdir -p $(TARGET_DIR)/usr/share/lazy/contracts
	cp -r $(@D)/docs/contracts/* $(TARGET_DIR)/usr/share/lazy/contracts/

	mkdir -p $(TARGET_DIR)/usr/share/lazy/models
	if [ -f "$(@D)/build/models/SmolLM2-360M-Instruct-Q4_K_M.gguf" ]; then \
		cp "$(@D)/build/models/SmolLM2-360M-Instruct-Q4_K_M.gguf" "$(TARGET_DIR)/usr/share/lazy/models/"; \
	fi

	mkdir -p $(TARGET_DIR)/etc/lazy/capabilities
	cp -r $(@D)/config/capabilities/* $(TARGET_DIR)/etc/lazy/capabilities/

	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	cp -r $(@D)/systemd/*.service $(TARGET_DIR)/etc/systemd/system/ 2>/dev/null || true
	cp -r $(@D)/systemd/*.slice $(TARGET_DIR)/etc/systemd/system/ 2>/dev/null || true
	for s in $(TARGET_DIR)/etc/systemd/system/lazy-*.service; do \
		[ -f "$$s" ] || continue; \
		b=`basename "$$s"`; \
		if echo "$$b" | grep -q "@"; then continue; fi; \
		if [ "$$b" = "lazy-first-boot.service" ]; then continue; fi; \
		ln -sf "/etc/systemd/system/$$b" "$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/$$b" 2>/dev/null || true; \
	done

	mkdir -p $(TARGET_DIR)/usr/bin
	install -m 0755 $(@D)/scripts/lazy-guest-daemon.py $(TARGET_DIR)/usr/bin/lazy-guest-daemon
endef

$(eval $(generic-package))
