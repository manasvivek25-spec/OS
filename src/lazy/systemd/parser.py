"""Parser for systemd unit files."""
from __future__ import annotations

import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ServiceUnit:
    """Structured representation of a systemd unit."""
    name: str
    path: Path
    sections: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def get(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        sec = self.sections.get(section, {})
        return sec.get(key, default)

    @property
    def unit(self) -> Dict[str, str]:
        return self.sections.get("Unit", {})

    @property
    def service(self) -> Dict[str, str]:
        return self.sections.get("Service", {})

    @property
    def install(self) -> Dict[str, str]:
        return self.sections.get("Install", {})


class SystemdUnitParser:
    """Parses systemd configuration files."""

    @staticmethod
    def parse_file(unit_path: Path | str) -> ServiceUnit:
        p = Path(unit_path)
        if not p.is_file():
            raise FileNotFoundError(f"Unit file not found: {p}")

        # Systemd files are similar to INI format, case-sensitive
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        cp.optionxform = str  # Preserve case for directives like NoNewPrivileges

        raw_content = p.read_text(encoding="utf-8", errors="replace")
        cp.read_string(raw_content)

        sections: Dict[str, Dict[str, str]] = {}
        for section in cp.sections():
            sections[section] = dict(cp.items(section))

        return ServiceUnit(name=p.name, path=p, sections=sections)

    @staticmethod
    def parse_directory(dir_path: Path | str) -> Dict[str, ServiceUnit]:
        """Parse all unit files in a directory."""
        d = Path(dir_path)
        units: Dict[str, ServiceUnit] = {}
        for f in sorted(d.glob("*.service")):
            units[f.name] = SystemdUnitParser.parse_file(f)
        return units
