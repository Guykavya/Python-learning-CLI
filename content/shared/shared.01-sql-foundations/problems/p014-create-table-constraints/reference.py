SCRIPT = """
CREATE TABLE members (
  member_id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name  TEXT NOT NULL,
  age   INTEGER CHECK (age >= 13),
  plan  TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro'))
);
"""
