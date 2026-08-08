import json
import logging
import sqlite3

from config.settings import server
from util import sqlite_migrations

logger = logging.getLogger(__name__)

connection = sqlite3.connect(
    server.sqlite_url,
    autocommit=True
)

connection.execute(
    'CREATE TABLE IF NOT EXISTS migrations (id INT PRIMARY KEY, name TEXT)'
)
current_version = (
    connection.execute('SELECT MAX(id) FROM migrations').fetchone()[0] or 0
)

migrations = sqlite_migrations.get_migrations()
latest_version = len(migrations)
for i in range(current_version, latest_version):
    connection.executescript(migrations[i])
    logger.info(
        'SQLite DB schema is updated to v%d',
        i + 1
    )


def to_device_dict(
    row
):
    if row is None:
        return None

    return {
        'id': row[0],
        'code': row[1],
        'refresh': row[2],
        'token': row[3],
        'settings': None if row[4] is None else json.loads(row[4]),
        'user_agent': row[5]
    }


def query_device(
    sql,
    params
):
    cursor = connection.execute(
        sql,
        params
    )

    return to_device_dict(
        cursor.fetchone()
    )


DEVICE_COLUMNS = 'id, code, refresh, token, settings, user_agent'


def get_device_by_id(
    device_id
):
    return query_device(
        f'SELECT {DEVICE_COLUMNS} FROM devices WHERE id = ?1',
        [device_id]
    )


def create_device(
    entry
):
    settings = entry.get('settings')
    return query_device(
        f"""
        INSERT INTO devices ({DEVICE_COLUMNS})
        VALUES (?1, ?2, ?3, ?4, ?5, ?6)
        RETURNING {DEVICE_COLUMNS}
        """,
        [
            entry.get('id'),
            entry.get('code'),
            entry.get('refresh'),
            entry.get('token'),
            None if settings is None else json.dumps(settings),
            entry.get('user_agent')
        ]
    )


def update_device_code(
    id,
    code
):
    return query_device(
        f'UPDATE devices SET code = ?2 WHERE id = ?1 RETURNING {DEVICE_COLUMNS}',
        [id, code]
    )


def update_device_tokens(
    id,
    token,
    refresh
):
    return query_device(
        f"""
        UPDATE devices SET token = ?2, refresh = ?3
        WHERE id = ?1 RETURNING {DEVICE_COLUMNS}
        """,
        [id, token, refresh]
    )


def update_tokens(
    token,
    new_token,
    refresh
):
    return query_device(
        f"""
        UPDATE devices SET token = ?2, refresh = ?3
        WHERE token = ?1 RETURNING {DEVICE_COLUMNS}
        """,
        [token, new_token, refresh]
    )


def delete_device(
    id
):
    return query_device(
        f'DELETE FROM devices WHERE id = ?1 RETURNING {DEVICE_COLUMNS}',
        [id]
    )


def update_device_user_agent(
    id,
    user_agent
):
    return query_device(
        f"""
        UPDATE devices SET user_agent = ?2
        WHERE id = ?1 RETURNING {DEVICE_COLUMNS}
        """,
        [id, user_agent]
    )


def update_device_settings(
    id,
    param
):
    return query_device(
        f"""
        UPDATE devices SET settings = ?2
        WHERE id = ?1 RETURNING {DEVICE_COLUMNS}
        """,
        [id, json.dumps(param)]
    )


def get_domain(
    domain
):
    cursor = connection.execute(
        'SELECT domain FROM domains WHERE domain = ?1',
        [domain]
    )

    row = cursor.fetchone()

    return None if row is None else row[0]


def get_domains():
    cursor = connection.execute('SELECT domain FROM domains')

    return [row[0] for row in cursor.fetchall()]


def add_domain(
    domain
):
    cursor = connection.execute(
        'INSERT INTO domains (domain) VALUES (?1) RETURNING domain',
        [domain]
    )
    row = cursor.fetchone()

    return None if row is None else row[0]
