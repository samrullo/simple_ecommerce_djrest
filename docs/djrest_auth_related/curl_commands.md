# To login

```bash
curl -X POST http://localhost:8000/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email": "samrullo@mail.com", "password": "mypassword"}'

```

# To logout

```bash
curl -X POST http://localhost:8000/auth/logout -H "Content-Type: application/json"
```

# To register

```bash
curl -X POST http://localhost:8000/auth/registration/ -H "Content-Type: application/json" -d '{"email":"samira@mail.com","password1":"kichkinas!r","password2":"kichkinas!r"}'
```


```bash
curl -X POST http://localhost:8000/auth/registration/ -H "Content-Type: application/json" -d '{"email": "naira@mail.com","password1": "kichk!nasir","password2": "kichk!nasir", "first_name": "Naira", "last_name": "Amrulloeva", "customer": {"phone": "1234567890"},"address": {"street": "Ushirohirai 170 ban 315 goshitu", "city": "Nagareyama","state": "Chiba","zip_code": "270-0151","country": "Japan","is_default": "true"}}'
```

# To get products 

```bash
curl -X GET http://localhost:8000/api/v1/api/product/ \
     -H "Authorization: Bearer <access_token>"
```


