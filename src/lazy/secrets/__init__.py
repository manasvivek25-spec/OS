"""Lazy OS Secrets Vault and Service (lazy-secrets, Rule F4)."""
from lazy.secrets.service import SecretsService, get_peer_creds
from lazy.secrets.vault import SecretAccessDenied, SecretVault

__all__ = ["SecretVault", "SecretAccessDenied", "SecretsService", "get_peer_creds"]
