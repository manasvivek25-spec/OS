"""GBNF grammar and schema constraints for Lazy OS intent generation."""
from __future__ import annotations

from typing import Any, Dict, List

# List of all 37 valid registered Lazy OS capabilities
CAPABILITIES = [
    "chat.read", "chat.send",
    "code.run", "code.write",
    "doc.create_docx", "doc.create_markdown",
    "fs.copy", "fs.delete", "fs.list", "fs.move", "fs.read", "fs.write",
    "hw.backlight_set", "hw.governor_set", "hw.power_profile_set", "hw.rfkill_set",
    "hw.usb_authorize", "hw.usb_list", "hw.volume_set",
    "mail.draft", "mail.list", "mail.read", "mail.send",
    "outbox.cancel",
    "sys.logs_read", "sys.process_list", "sys.process_signal",
    "sys.service_restart", "sys.service_status", "sys.setting_set",
    "task.undo",
    "web.click", "web.download", "web.fill", "web.navigate", "web.read", "web.submit",
]


def generate_intent_gbnf_grammar(capabilities: List[str] = CAPABILITIES) -> str:
    """Generate a strict GBNF grammar forcing output to match Lazy OS Intent schema."""
    caps_rule = " | ".join(f'\'"{cap}"\'' for cap in sorted(capabilities))

    grammar = f"""root ::= ws intent ws
intent ::= "{{" ws "\\"id\\":" ws string "," ws "\\"ts\\":" ws string "," ws "\\"task_id\\":" ws string "," ws "\\"requester\\":" ws requester "," ws "\\"capability\\":" ws capability "," ws "\\"params\\":" ws object "," ws "\\"provenance\\":" ws provenance ws "}}"
requester ::= "\\"voice\\"" | "\\"text\\"" | "\\"hud\\"" | "\\"routine\\""
capability ::= {caps_rule}
provenance ::= "[" ws provenance-item ("," ws provenance-item)* ws "]"
provenance-item ::= "{{" ws "\\"source\\":" ws string "," ws "\\"trusted\\":" ws boolean ("," ws "\\"detail\\":" ws string)? ws "}}"

value  ::= object | array | string | number | boolean | null
object ::= "{{" ws (string ":" ws value ("," ws string ":" ws value)*)? ws "}}"
array  ::= "[" ws (value ("," ws value)*)? ws "]"
string ::= "\\"" ([^"\\\\\x00-\x1f] | "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\\""
number ::= ("-"? [0-9]+ ("." [0-9]+)? ([eE] [-+]? [0-9]+)?)
boolean ::= "true" | "false"
null ::= "null"
ws ::= [ \\t\\n\\r]*
"""
    return grammar


INTENT_GBNF: str = generate_intent_gbnf_grammar()


def get_intent_gbnf() -> str:
    """Return the cached Intent GBNF grammar string."""
    return INTENT_GBNF
