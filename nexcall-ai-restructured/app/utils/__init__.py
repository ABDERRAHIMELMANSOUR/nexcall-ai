"""
NexCall AI — Utilitaires
Fonctions helpers réutilisables.
"""
from datetime import datetime


def format_duration(seconds: int) -> str:
    """Formate une durée en secondes en format lisible."""
    if not seconds:
        return "0s"
    m, s = divmod(seconds, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


def format_datetime(dt: datetime) -> str:
    """Formate un datetime en format français."""
    if not dt:
        return "—"
    return dt.strftime("%d/%m/%Y %H:%M")
