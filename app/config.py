"""Configuration applicative lue depuis l'environnement (approche 12-factor).

Aucune valeur secrète en dur : tout provient des variables d'environnement,
elles-mêmes injectées par docker-compose / le fichier .env.
"""
from __future__ import annotations

import functools
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    # --- PostgreSQL ---
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_pool_min: int
    db_pool_max: int
    db_connect_timeout: int

    # --- Réseau / sniffer ---
    capture_interface: Optional[str]  # None = interface auto de Scapy
    capture_bpf_filter: str  # filtre BPF
    capture_debug_dump: Optional[str]  # chemin fichier : dumpe les messages EL bruts

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            db_host=os.getenv("DB_HOST", "127.0.0.1"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "dofus"),
            db_user=os.getenv("DB_USER", "dofus"),
            db_password=os.getenv("DB_PASSWORD", "dofus"),
            db_pool_min=int(os.getenv("DB_POOL_MIN", "1")),
            db_pool_max=int(os.getenv("DB_POOL_MAX", "5")),
            db_connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
            capture_interface=os.getenv("CAPTURE_INTERFACE") or None,
            # Dofus Retro officiel : trafic de jeu EN CLAIR sur le port 443
            # (protocole texte, pas TLS). Filtre volontairement large ; on ne
            # retient que les messages d'en-tête 'EL' côté décodage.
            capture_bpf_filter=os.getenv("CAPTURE_BPF_FILTER", "tcp port 443"),
            capture_debug_dump=os.getenv("CAPTURE_DEBUG_DUMP") or None,
        )


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton de configuration (mémoïsé pour tout le process)."""
    return Settings.from_env()
