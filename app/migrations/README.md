# 🧬 Alembic Usage

## 🔹 Create a new migration
```bash
alembic revision --autogenerate -m "describe your change" --rev-id <revision_id>
```

---

## 🔹 Apply migrations
Run all new migrations:
```bash
alembic upgrade head
```

Migrate to a specific version:
```bash
alembic upgrade <revision_id>
```

---

## 🔹 Rollback migrations
Undo the last migration:
```bash
alembic downgrade -1
```

Revert to a specific version:
```bash
alembic downgrade <revision_id>
```

---

## 🔹 Check migration status
Show current DB revision:
```bash
alembic current
```

List migration history:
```bash
alembic history
```

---

## 🔹 Stamp database (mark version without running migrations)
```bash
alembic stamp head
```

---

## 🔹 Run migrations automatically (CI/CD, startup script, etc.)
```bash
alembic upgrade head
```
