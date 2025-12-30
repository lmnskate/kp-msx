def get_migrations():
  return [
    '''
    CREATE TABLE IF NOT EXISTS devices (
        id TEXT PRIMARY KEY,
        code TEXT,
        refresh TEXT,
        token TEXT,
        settings JSONB NULL,
        user_agent TEXT NULL
    );

    CREATE TABLE IF NOT EXISTS domains (domain TEXT PRIMARY KEY);
    INSERT OR IGNORE INTO migrations VALUES (1, \'initial\');
    '''
  ]
