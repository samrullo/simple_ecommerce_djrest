Great! Here's a `render.yaml` file tailored for your **Simple Ecommerce Django REST app using Docker**, including the proper `preDeployCommand` for migrations and static collection:

---

### ✅ `render.yaml` (Place this in your project root)

```yaml
services:
  - type: web
    name: simple-ecommerce
    env: docker
    plan: free  # or change to 'starter' / 'pro' if applicable
    region: oregon
    dockerfilePath: ./Dockerfile  # Or DockerfileLocal.dockerfile if that’s what you're using
    buildCommand: ""  # Not needed for Docker services
    startCommand: gunicorn config.wsgi:application --bind 0.0.0.0:8000

    # This will run before each deploy
    preDeployCommand: |
      python manage.py migrate
      python manage.py collectstatic --noinput
```

---

### ✅ Notes

* `dockerfilePath`: if you're using a custom Dockerfile like `DockerfileLocal.dockerfile`, change this:

  ```yaml
  dockerfilePath: ./DockerfileLocal.dockerfile
  ```
* `buildCommand` is empty because Docker handles builds with the file directly.
* `startCommand` overrides any `CMD` in your Dockerfile during Render deploy.
* `preDeployCommand` will ensure:

  * DB migrations are applied.
  * Static files are collected (so admin panel works correctly with Whitenoise or other static handler).

---

### Optional: Add `.dockerignore`

To avoid copying unnecessary files into the image:

```
__pycache__/
*.pyc
*.pyo
*.pyd
venv/
.env
db.sqlite3
media/
staticfiles/
pgdata/
```

---

Would you also like a `Dockerfile.production` with Whitenoise preconfigured for static file serving, or are you handling static files another way (e.g. S3, Nginx)?
