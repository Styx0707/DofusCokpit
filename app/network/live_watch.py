"""Watcher de dossier pour le suivi « live » des repops.

Un ring-buffer dumpcap (côté hôte Windows, là où la carte réseau est visible)
écrit des fichiers .pcapng courts dans un dossier partagé (volume Docker). Ce
watcher, lancé dans le process de l'API, ingère chaque fichier dès qu'il est
« stabilisé » (plus écrit depuis `settle_s`) et alimente le RepopMonitor.

Pourquoi ce détour : un conteneur Docker Desktop ne peut pas sniffer la carte
réseau de l'hôte ; on délègue donc la capture à dumpcap et on ne partage que les
fichiers. Latence ≈ durée d'un fichier + settle (quelques secondes) — largement
suffisant pour du repop (échelle minute).

Commande de capture côté hôte (PowerShell), ring de fichiers de 5 s :
    dumpcap -i <iface> -f "tcp port 443" -b duration:5 -b files:50 -w data\live\dofus.pcapng
"""
from __future__ import annotations

import glob
import logging
import os
import threading
import time
from typing import Dict, Optional

from app.core.repop_monitor import RepopMonitor

logger = logging.getLogger(__name__)


def _mtime(path: str) -> float:
    """mtime tolérant : 0.0 si le fichier a disparu (ring-buffer dumpcap)."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0


def watch_dir(
        monitor: RepopMonitor,
        directory: str,
        settle_s: float = 0.5,
        poll_s: float = 0.5,
        stop: Optional[threading.Event] = None,
        on_bank=None,
        on_prices=None,
) -> None:
    """Boucle de surveillance (bloquante) : à lancer dans un thread daemon.

    `on_bank` / `on_prices` (optionnels) sont transmis à ``feed_pcap`` : auto-sync
    de la banque (message ``EL``) et des prix HDV (messages ``EHP``/``EHl``) dès
    qu'ils apparaissent dans un fichier du ring-buffer."""
    logger.info("Watcher live actif sur %s (settle=%ss, poll=%ss)",
                directory, settle_s, poll_s)
    seen: Dict[str, float] = {}   # chemin -> mtime déjà ingéré
    while stop is None or not stop.is_set():
        try:
            _scan_once(monitor, directory, settle_s, seen, on_bank=on_bank, on_prices=on_prices)
        except Exception:
            # ne JAMAIS laisser une erreur tuer le thread (ex course avec le
            # ring-buffer dumpcap qui supprime un fichier en plein scan).
            logger.exception("Watcher : scan échoué (on continue).")
        time.sleep(poll_s)


def _scan_once(monitor: RepopMonitor, directory: str, settle_s: float,
               seen: Dict[str, float], max_per_scan: int = 6, on_bank=None, on_prices=None) -> None:
    patterns = (os.path.join(directory, "*.pcapng"),
                os.path.join(directory, "*.pcap"))
    files = sorted((f for pat in patterns for f in glob.glob(pat)),
                   key=_mtime)
    # candidats : stabilisés (plus écrits depuis settle_s) et pas déjà ingérés
    todo = []
    for path in files:
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if time.time() - mtime < settle_s or seen.get(path) == mtime:
            continue
        todo.append((path, mtime))

    # ANTI-RETARD : scapy est lent (~qq s / fichier de 2 Mo). Si un backlog se
    # forme, on ne traite que les fichiers les PLUS RÉCENTS. Les fichiers traités
    # ET sautés sont SUPPRIMÉS : ça borne le dossier (le ring dumpcap n'etait pas
    # borné -> 800+ fichiers accumulés -> chaque reload relançait un skip-storm
    # qui faisait perdre les PM de combat). Dossier petit = watcher toujours à
    # jour, PM captés au début du combat -> « qui joue » fiable pour tous.
    skipped = []
    if len(todo) > max_per_scan:
        skipped = todo[:-max_per_scan]
        todo = todo[-max_per_scan:]
        logger.warning("Watcher en retard : %d fichiers sautés (puis supprimés).",
                       len(skipped))

    for path, mtime in todo:
        try:
            from app.network.pcap_feed import feed_pcap
            summary = feed_pcap(monitor, path, on_bank=on_bank, on_prices=on_prices)
            logger.info("Live ingest %s : %s", os.path.basename(path), summary)
        except Exception:
            logger.exception("Échec ingestion live de %s", path)
        finally:
            _discard(path, seen)

    for path, _ in skipped:   # backlog : jeté pour rester courant et borner le dossier
        _discard(path, seen)


def _discard(path: str, seen: Dict[str, float]) -> None:
    """Supprime un fichier de capture déjà traité/sauté (ring éphémère). Retombe
    sur un simple marquage 'vu' si la suppression échoue (fichier verrouillé)."""
    try:
        os.remove(path)
    except OSError:
        try:
            seen[path] = os.path.getmtime(path)
        except OSError:
            pass


def start_watcher(monitor: RepopMonitor, directory: str, on_bank=None, on_prices=None) -> threading.Event:
    """Démarre le watcher dans un thread daemon. Retourne l'Event d'arrêt.

    `on_bank` / `on_prices` (optionnels) : callbacks d'auto-sync de la banque
    (message ``EL``) et des prix HDV (messages ``EHP``/``EHl``)."""
    stop = threading.Event()
    thread = threading.Thread(
        target=watch_dir, args=(monitor, directory),
        kwargs={"stop": stop, "on_bank": on_bank, "on_prices": on_prices},
        name="live-watch", daemon=True,
    )
    thread.start()
    return stop
