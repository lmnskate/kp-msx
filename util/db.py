import json
import sqlite3

import config
from util import sqlite_migrations

connection = sqlite3.connect(config.SQLITE_URL, autocommit=True)

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
    print(f'SQLite DB schema is updated to v{i + 1}')


def _to_device_dict(row):
    if row is None:
        return None
    return {
        'id': row[0],
        'code': row[1],
        'refresh': row[2],
        'token': row[3],
        'settings': None if row[4] is None else json.loads(row[4]),
        'user_agent': row[5],
    }


def _query_device(sql, params):
    cursor = connection.execute(sql, params)
    return _to_device_dict(cursor.fetchone())


_DEVICE_COLUMNS = 'id, code, refresh, token, settings, user_agent'


def get_device_by_id(device_id):
    return _query_device(
        f'SELECT {_DEVICE_COLUMNS} FROM devices WHERE id = ?1',
        [device_id],
    )


def create_device(entry):
    settings = entry.get('settings')
    return _query_device(
        f"""
        INSERT INTO devices ({_DEVICE_COLUMNS})
        VALUES (?1, ?2, ?3, ?4, ?5, ?6)
        RETURNING {_DEVICE_COLUMNS}
        """,
        [
            entry.get('id'),
            entry.get('code'),
            entry.get('refresh'),
            entry.get('token'),
            None if settings is None else json.dumps(settings),
            entry.get('user_agent'),
        ],
    )


def update_device_code(id, code):
    return _query_device(
        f'UPDATE devices SET code = ?2 WHERE id = ?1 RETURNING {_DEVICE_COLUMNS}',
        [id, code],
    )


def update_device_tokens(id, token, refresh):
    return _query_device(
        f"""
        UPDATE devices SET token = ?2, refresh = ?3
        WHERE id = ?1 RETURNING {_DEVICE_COLUMNS}
        """,
        [id, token, refresh],
    )


def update_tokens(token, new_token, refresh):
    return _query_device(
        f"""
        UPDATE devices SET token = ?2, refresh = ?3
        WHERE token = ?1 RETURNING {_DEVICE_COLUMNS}
        """,
        [token, new_token, refresh],
    )


def delete_device(id):
    return _query_device(
        f'DELETE FROM devices WHERE id = ?1 RETURNING {_DEVICE_COLUMNS}',
        [id],
    )


def update_device_user_agent(id, user_agent):
    return _query_device(
        f"""
        UPDATE devices SET user_agent = ?2
        WHERE id = ?1 RETURNING {_DEVICE_COLUMNS}
        """,
        [id, user_agent],
    )


def update_device_settings(id, param):
    return _query_device(
        f"""
        UPDATE devices SET settings = ?2
        WHERE id = ?1 RETURNING {_DEVICE_COLUMNS}
        """,
        [id, json.dumps(param)],
    )


def get_domain(domain):
    cursor = connection.execute(
        'SELECT domain FROM domains WHERE domain = ?1',
        [domain],
    )
    row = cursor.fetchone()
    return None if row is None else row[0]


def add_domain(domain):
    cursor = connection.execute(
        'INSERT INTO domains (domain) VALUES (?1) RETURNING domain',
        [domain],
    )
    row = cursor.fetchone()
    return None if row is None else row[0]
