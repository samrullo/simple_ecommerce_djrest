# How to set media to aws s3
You're looking at a **production-grade solution** for hosting Django media files on **Amazon S3** using the `django-storages` library. This is a widely used and reliable approach — especially on ephemeral hosting platforms like **Render**, **Heroku**, or **Vercel** where the local disk is not persistent.

---

## ✅ What this setup does

It tells Django:

> “Instead of saving uploaded media files to the local `MEDIA_ROOT`, upload them directly to an S3 bucket and serve them from there.”

---

## 🔧 Key Configuration Explained

```python
INSTALLED_APPS += ["storages"]
```

Enables the `django-storages` package, which integrates S3 as a backend for file storage.

```python
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
```

Tells Django to use S3 as the backend for all uploaded files (i.e., `ImageField`, `FileField`, etc.).

---

## 🔐 AWS Credentials

```python
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
```

Store these in your `.env` or your Render Dashboard → **Environment Variables**.

---

## 🪣 Bucket Info

```python
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = "ap-northeast-1"
```

* This points to the S3 bucket where files will be uploaded.
* Make sure the bucket exists and has proper permissions.

---

## 🔄 Overwrite Behavior

```python
AWS_S3_FILE_OVERWRITE = False
```

Ensures that uploaded files with the same name don’t overwrite each other.

---

## 🔐 Permissions

```python
AWS_DEFAULT_ACL = None
```

This prevents Django from applying deprecated default ACLs like `public-read`. You’ll manage permissions via **bucket policy** or **CloudFront/Signed URLs** instead.

---

## 🌐 Media URL

```python
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
```

Your frontend will fetch uploaded images from this URL.

👉 If you're using **CloudFront**, replace with:

```python
MEDIA_URL = "https://cdn.yourdomain.com/"
```

---

## 📦 Installation

Make sure you have these installed in your project:

```bash
pip install boto3 django-storages
```

And listed in `pyproject.toml` or `requirements.txt` if you're using Docker + uv.

---

## 🧪 Optional – Test Uploads

In your admin or anywhere you upload `models.ImageField` or `models.FileField`, uploaded files will now go to S3 and be accessible at:

```
https://<your-bucket>.s3.amazonaws.com/media/some-image.jpg
```

---

## 🧰 Optional Tips

* Use S3 bucket **folder prefixing** by subclassing the storage class:

```python
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
```

And use:

```python
DEFAULT_FILE_STORAGE = "yourapp.storage_backends.MediaStorage"
```

* For **public-read** access to files, make sure your bucket policy allows it.
* For **private files**, consider signed URLs or CloudFront with restricted access.

---

Would you like a working `storage_backends.py` or example `bucket policy` too?

# Where to save CustomeStorage class
A good practice is to save this custom S3 storage class in a dedicated file, typically named something like:

your_project/
├── your_app/
│   └── storage_backends.py

✅ So for example:

If your app is named ecommerce, save it as:

ecommerce/storage_backends.py

📄 Contents of storage_backends.py:

from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False

🛠️ In settings.py, configure:

DEFAULT_FILE_STORAGE = "ecommerce.storage_backends.MediaStorage"

(Replace "ecommerce" with the actual name of your Django app if different.)

⸻

🧪 Why this is good practice:
	•	Keeps settings modular and clean
	•	Makes it easy to create multiple storage backends later (e.g. StaticStorage, PrivateMediaStorage)
	•	Follows the Django convention of organizing reusable code per app

⸻

If you also want to manage static files through S3/CDN in the future, you can add:

class StaticStorage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"

And then set in settings.py:

STATICFILES_STORAGE = "ecommerce.storage_backends.StaticStorage"

Let me know if you want full example of separating static and media in S3!

# Store media under s3 bucket dedicated folder
Great idea! If you want to organize your files in S3 so that all uploads go under a folder called ecommerce/media/, you can simply customize your storage backend’s location.

⸻

✅ Step-by-step

1. Create storage_backends.py (if you haven’t yet):

from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = "ecommerce/media"  # this will store files under ecommerce/media/
    file_overwrite = False

2. Update settings.py:

DEFAULT_FILE_STORAGE = "ecommerce.storage_backends.MediaStorage"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = "ap-northeast-1"  # change to your actual AWS region
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/ecommerce/media/"


⸻

📝 Example File Path

If you upload a product image named shoe.jpg, it will be stored in:

s3://your-bucket-name/ecommerce/media/shoe.jpg

And publicly accessible via:

https://your-bucket-name.s3.ap-northeast-1.amazonaws.com/ecommerce/media/shoe.jpg


⸻

💡 Pro Tips
	•	If you’re handling user uploads, it’s a good idea to prefix file paths with something like products/, e.g.:

def upload_to(instance, filename):
    return f"products/{instance.id}/{filename}"

Then in your model:

image = models.ImageField(upload_to=upload_to)

So the full path becomes:

ecommerce/media/products/123/shoe.jpg


	•	You can also create multiple storage backends (e.g., PublicMediaStorage, PrivateMediaStorage) if you want to restrict access.

Let me know if you want a helper to generate unique paths for images or restrict access to uploads!