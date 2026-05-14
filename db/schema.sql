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

CREATE TABLE IF NOT EXISTS events (
    id          SERIAL       PRIMARY KEY,
    title       VARCHAR(256) NOT NULL,
    description TEXT,
    starts_at   TIMESTAMP    NOT NULL,
    ends_at     TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_participants (
    event_id      INT          NOT NULL,
    username      VARCHAR(128) NOT NULL,
    registered_at TIMESTAMP    NOT NULL DEFAULT NOW(),
    PRIMARY KEY (event_id, username),
    CONSTRAINT fk_ep_event FOREIGN KEY (event_id) REFERENCES events (id),
    CONSTRAINT fk_ep_user  FOREIGN KEY (username)  REFERENCES users (username)
);
