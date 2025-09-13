# Settings to server static files from S3
When I specified ```STORAGES``` dictionary as below, Django will look for static files such as css,js in S3 bucket folder.

```python
STORAGES = {
    # 'default' is the key used for models.FileField and models.ImageField
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            # AWS credentials and bucket name are still needed globally
            "bucket_name": "elasticbeanstalk-us-west-2-384482548730",
            # Other options can be specified here to override global settings
            "location": "ecommerce/media", # Optional: Adds a path prefix within the bucket
            "default_acl": "public-read", # Optional: Sets default permissions
        },
    },
    # 'staticfiles' is the key used by Django's collectstatic command
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        "OPTIONS": {
            # Specific options for static files
            "bucket_name": "elasticbeanstalk-us-west-2-384482548730",
            "location": "ecommerce/static", # A path prefix for static files
            "default_acl":"public-read"
        },
    },
}

```

So when I deployed djange rest app to Render and tried accessing /admin page, it showed no styles
because there were no css files in S3 bucket location.

I had to specify following variables in ```settings.py```

```python
AWS_S3_CUSTOM_DOMAIN = f'{STORAGES["staticfiles"]["OPTIONS"]["bucket_name"]}.s3.amazonaws.com'

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STORAGES['staticfiles']['OPTIONS']['location']}/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STORAGES['default']['OPTIONS']['location']}/"

```

And then run ```collecstatic``` to copy css,js files to S3 bucket location

```bash
python manage.py collectstatic --noinput
```