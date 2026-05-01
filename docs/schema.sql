-- SentinelStream Core Schema (3NF with analytics-friendly dimensions)

CREATE TABLE IF NOT EXISTS user_profiles (
    id VARCHAR(64) PRIMARY KEY,
    home_country CHAR(2) NOT NULL DEFAULT 'US',
    current_balance NUMERIC(14,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fraud_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    expression TEXT NOT NULL,
    risk_weight NUMERIC(4,3) NOT NULL DEFAULT 0.150,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES user_profiles(id),
    merchant_id VARCHAR(64) NOT NULL,
    amount NUMERIC(14,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    country CHAR(2) NOT NULL,
    status VARCHAR(16) NOT NULL,
    risk_score NUMERIC(4,3) NOT NULL,
    triggered_rules JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS idempotency_records (
    key VARCHAR(128) PRIMARY KEY,
    request_hash CHAR(64) NOT NULL,
    response_payload JSONB NOT NULL,
    status_code INTEGER NOT NULL DEFAULT 200,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tx_user_created_at ON transactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tx_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_idempotency_created_at ON idempotency_records(created_at DESC);

-- Optional star-schema projection for analytics warehouse:
-- dim_user, dim_merchant, dim_geo, fact_transaction_fraud
