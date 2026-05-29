# SQL migrations

Place versioned SQL files in this folder, for example:
- 001_add_order_indexes.sql
- 002_add_admin_audit_table.sql

Migrations are applied automatically during app startup via init_db().
Already applied files are tracked in the schema_migrations table.

You can also run migrations manually:

python -m data.migrate
