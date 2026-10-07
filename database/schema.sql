CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'analyst' CHECK (role IN ('admin','analyst','viewer')),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE industries (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  default_rate NUMERIC(6,2) NOT NULL
);

CREATE TABLE machines (
  id SERIAL PRIMARY KEY,
  industry_id TEXT REFERENCES industries(id),
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  power_kw NUMERIC(8,2) NOT NULL,
  efficiency NUMERIC(5,2) NOT NULL,
  UNIQUE (industry_id, code)
);

CREATE TABLE bills (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  industry TEXT NOT NULL,
  consumer_number TEXT,
  billing_date TEXT,
  tariff TEXT,
  units DOUBLE PRECISION NOT NULL,
  amount DOUBLE PRECISION NOT NULL,
  days INT NOT NULL DEFAULT 30,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_bills_user_industry ON bills (user_id, industry);

CREATE TABLE analyses (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  bill_id INT REFERENCES bills(id) ON DELETE CASCADE,
  result JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);