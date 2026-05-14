-- F5 APM SQL Auth – initial schema
-- Compatible with PostgreSQL 14+, MySQL 8+

CREATE TABLE IF NOT EXISTS users (
    username     VARCHAR(128) PRIMARY KEY,
    password_hash VARCHAR(256) NOT NULL,
    full_name    VARCHAR(256),
    email        VARCHAR(256),
    enabled      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_login   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_enabled ON users (enabled);
