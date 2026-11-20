INDEXES = [
    "CREATE INDEX idx_users_email_lower ON users(lower(email))",
    "CREATE INDEX idx_tickets_open ON tickets(created) WHERE status = 'open'",
]
