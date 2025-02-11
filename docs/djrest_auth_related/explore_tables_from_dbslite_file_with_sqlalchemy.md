# How to explore tables from db.sqlite3 file

Using below code

```python
from sqlalchemy import create_engine, Table, MetaData
import pathlib

dbpath=pathlib.Path.cwd()/"db.sqlite3"
db_uri=f"sqlite:///{dbpath}"
engine=create_engine(db_uri)

meta = MetaData()
meta.reflect(bind=engine)

tables = {table.name: table for table in list(meta.tables.values())}

```

Tables returned

```python
['account_emailaddress',
 'auth_user',
 'account_emailconfirmation',
 'auth_group',
 'auth_group_permissions',
 'auth_permission',
 'django_content_type',
 'auth_user_groups',
 'auth_user_user_permissions',
 'authtoken_token',
 'django_admin_log',
 'django_migrations',
 'django_session',
 'socialaccount_socialaccount',
 'socialaccount_socialapp',
 'socialaccount_socialtoken']
```

# To explore columns of Table

```python
[col for col in tables["auth_user"].columns]
```

- ```auth_user``` columns

```python
[Column('id', INTEGER(), table=<auth_user>, primary_key=True, nullable=False),
 Column('password', VARCHAR(length=128), table=<auth_user>, nullable=False),
 Column('last_login', DATETIME(), table=<auth_user>),
 Column('is_superuser', BOOLEAN(), table=<auth_user>, nullable=False),
 Column('username', VARCHAR(length=150), table=<auth_user>, nullable=False),
 Column('last_name', VARCHAR(length=150), table=<auth_user>, nullable=False),
 Column('email', VARCHAR(length=254), table=<auth_user>, nullable=False),
 Column('is_staff', BOOLEAN(), table=<auth_user>, nullable=False),
 Column('is_active', BOOLEAN(), table=<auth_user>, nullable=False),
 Column('date_joined', DATETIME(), table=<auth_user>, nullable=False),
 Column('first_name', VARCHAR(length=150), table=<auth_user>, nullable=False)]
```

- ```account_emailaddress``` columns

```python
[
 Column('id', INTEGER(), table=<account_emailaddress>, primary_key=True, nullable=False),
 Column('verified', BOOLEAN(), table=<account_emailaddress>, nullable=False),
 Column('primary', BOOLEAN(), table=<account_emailaddress>, nullable=False),
 Column('user_id', INTEGER(), ForeignKey('auth_user.id'), table=<account_emailaddress>, nullable=False),
 Column('email', VARCHAR(length=254), table=<account_emailaddress>, nullable=False)
]
```