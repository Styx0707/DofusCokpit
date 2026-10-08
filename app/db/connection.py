"""Gestion centralisée des connexions PostgreSQL.

- Pool de connexions (ThreadedConnectionPool) pour supporter à terme un
  serveur API multi-thread.
- Context managers pour garantir la libération des connexions et la
  cohérence transactionnelle (commit/rollback automatiques).
"""
from __future__ import annotations

import contextlib
import logging
import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extensions import cursor as PgCursor
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from typing import Iterator, Optional

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_pool: Optional[ThreadedConnectionPool] = None


def init_pool(settings: Optional[Settings] = None) -> ThreadedConnectionPool:
    """Initialise (une seule fois) le pool de connexions."""
    global _pool
    if _pool is not None:
        return _pool
    settings = settings or get_settings()
    logger.info(
        "Initialisation du pool PostgreSQL -> %s:%s/%s",
        settings.db_host, settings.db_port, settings.db_name,
    )
    _pool = ThreadedConnectionPool(
        minconn=settings.db_pool_min,
        maxconn=settings.db_pool_max,
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=settings.db_connect_timeout,
    )
    return _pool


def close_pool() -> None:
    """Ferme proprement toutes les connexions du pool (à appeler au shutdown)."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
        logger.info("Pool PostgreSQL fermé.")


@contextlib.contextmanager
def get_connection() -> Iterator[PgConnection]:
    """Emprunte une connexion au pool et la restitue systématiquement."""
    pool = init_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


@contextlib.contextmanager
def transaction(commit: bool = True) -> Iterator[PgCursor]:
    """Fournit un curseur RealDict dans une transaction gérée.

    - commit=True  : COMMIT si le bloc réussit, ROLLBACK sur exception.
    - commit=False : lecture seule (aucun COMMIT), ROLLBACK sur exception.
    Le curseur et la connexion sont toujours libérés.
    """
    with get_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("Transaction annulée (rollback).")
            raise
        finally:
            cur.close()
