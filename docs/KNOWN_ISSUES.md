# Known Issues and Deviations

## Tracked Tradeoffs & Documented Fallbacks

### ISSUE-001: Monolithic Browser (Chromium/WebKit) Image Footprint vs. 40% Distro Size Reduction
- **Reference**: Prompt Section 4 Defaults & Milestone M5.5.
- **Description**: Monolithic GUI web browsers (e.g. `meta-browser` Chromium or WebKitGTK) add >450 MB compressed rootfs overhead, along with hundreds of graphical dependencies (Wayland/X11, Mesa, LLVM, Rust, GStreamer), violating the university Track A OS project constraint of maintaining a >=40% image size reduction versus standard distributions (Debian 12 minimal baseline).
- **Resolution / Fallback**: Implemented the Section 4 documented fallback:
  1. `meta-lazy` packages `lazy-browser` providing the headless WebDriver client and pure-Python isolated sandbox DOM driver.
  2. Full browser integration is verified on the host and in QEMU via WebDriver and `PurePythonBrowserDriver`.
  3. `WebBroker` transparently supports both engines via `BaseBrowserDriver` and `get_browser_driver()`.
  4. All web capabilities (`web.read`, `web.navigate`, `web.click`, `web.fill`, `web.submit`, `web.download`) pass 100% of functional and security injection tests.
