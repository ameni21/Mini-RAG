## Run Alembic Migration 

### Configuration 

```bash
cp alembic.ini.example alembic.ini
```
- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)

### (Optional) create a new migration

```bash
alembic revision --autogenerate -m "ADD ... commit"
```
### Upgrade the database 

```bash 
alembic upgrade head
```

