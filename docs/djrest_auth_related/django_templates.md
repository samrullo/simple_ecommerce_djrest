# How to organize templates folder

In Django, you have a couple of common options for where to place your `templates` folder:

---

### 1. At the Project Level

A common practice is to create a single `templates` folder at the root of your project (i.e., next to your `manage.py` file). Then, in your project's `settings.py`, add that folder to the template search path.

**Steps:**

1. **Create the folder:**

   At the root of your project (alongside `manage.py`), create a directory called `templates`.

2. **Configure `settings.py`:**

   In your `settings.py`, locate the `TEMPLATES` setting and add the path to your templates folder. For example:

   ```python
   import os
   from pathlib import Path

   BASE_DIR = Path(__file__).resolve().parent.parent

   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [os.path.join(BASE_DIR, 'templates')],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
               ],
           },
       },
   ]
   ```

   This configuration tells Django to look for templates in the `templates` folder at your project root, in addition to the templates located within individual apps (if any).

3. **Organize Your Templates:**

   Inside the `templates` folder, you can organize your templates into subfolders. For example, if you're overriding the email confirmation template for dj_rest_auth/django-allauth, you might create:

   ```
   templates/
       account/
           email/
               email_confirm.html
   ```

---

### 2. Inside Each App

Alternatively, you can place a `templates` folder inside each Django app. This is useful for keeping templates closely associated with the app they belong to.

**Steps:**

1. **Create the folder within your app:**

   For example, if your app is named `accounts`, create:

   ```
   accounts/
       templates/
           accounts/
               email_confirm.html
   ```

2. **Ensure `APP_DIRS` is Enabled:**

   Make sure your `TEMPLATES` setting in `settings.py` has `'APP_DIRS': True,` so that Django automatically looks for a `templates` folder inside each app.

   ```python
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [],  # or you can still include a project-level templates folder here
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   # your context processors
               ],
           },
       },
   ]
   ```

   With `'APP_DIRS': True`, Django will search for templates inside any `templates` folder that resides within your apps.

---

### Which Approach to Use?

- **Project-level templates:**  
  This approach centralizes your templates and is often used when you have a shared design or layout that spans across multiple apps.

- **App-specific templates:**  
  This approach keeps templates bundled with the app, making the app more self-contained and reusable.

You can also mix both approaches. For example, you might use a project-level `templates` folder for base layouts and common templates, while keeping app-specific templates within the respective app folders.

---

By choosing one of these approaches and configuring your `TEMPLATES` setting appropriately, Django will be able to find your templates when rendering views.


# What are context processors? What they are used for?

In Django, **context processors** are functions that inject common variables into the context of every template rendered using Django’s template engine. This means you don’t have to manually pass these variables from each view—they become globally available in your templates.

### How They Work

1. **Definition:**  
   A context processor is simply a Python function that takes a `request` object as its parameter and returns a dictionary of key-value pairs. Each key-value pair in the dictionary becomes available in the context of your template.

2. **Configuration:**  
   In your `settings.py`, under the `TEMPLATES` setting, there’s an `OPTIONS` key that includes a list called `context_processors`. This list contains references to context processor functions. For example:

   ```python
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [os.path.join(BASE_DIR, 'templates')],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
                   # You can add your custom context processors here
               ],
           },
       },
   ]
   ```

3. **Usage:**  
   When Django renders a template, it automatically calls each of the context processors listed in the settings. The returned dictionaries are merged into the template’s context, making their data accessible in the template without having to pass it explicitly from the view.

### Common Built-in Context Processors

- **`django.template.context_processors.debug`:**  
  Adds debug-related variables to the context. This is typically only enabled when `DEBUG=True`.

- **`django.template.context_processors.request`:**  
  Makes the current `HttpRequest` object available in your templates as the variable `request`. This is useful for accessing request data or checking user attributes.

- **`django.contrib.auth.context_processors.auth`:**  
  Provides information about the currently authenticated user (as `user`) and other authentication-related variables. This allows you to easily check user permissions, login status, etc., in your templates.

- **`django.contrib.messages.context_processors.messages`:**  
  Adds any messages (using Django’s messaging framework) to the context, so they can be displayed in your templates.

### Why Use Context Processors?

- **Avoid Repetition:**  
  Instead of manually passing common data (like the current user, site settings, or other global information) in every view, a context processor does it once for all templates.

- **Cleaner Views:**  
  Your view functions remain focused on handling request-specific logic, without cluttering them with extra context data that is needed across many templates.

- **Consistency:**  
  Ensures that certain variables are always available in every template, leading to more consistent behavior across your application.

### Creating a Custom Context Processor

If you have data that you want available in every template—say, a site-wide setting or configuration—you can create your own context processor. For example:

1. **Define the context processor:**

   ```python
   # myapp/context_processors.py
   def site_settings(request):
       # Imagine you have some logic to fetch settings
       settings_data = {
           'SITE_NAME': 'My Awesome Site',
           'SUPPORT_EMAIL': 'support@example.com',
       }
       return settings_data
   ```

2. **Add it to your settings:**

   ```python
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [os.path.join(BASE_DIR, 'templates')],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
                   'myapp.context_processors.site_settings',  # Add your custom processor here
               ],
           },
       },
   ]
   ```

3. **Use it in your template:**

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <title>{{ SITE_NAME }}</title>
   </head>
   <body>
       <h1>Welcome to {{ SITE_NAME }}</h1>
       <p>For support, contact: {{ SUPPORT_EMAIL }}</p>
   </body>
   </html>
   ```

This way, every time a template is rendered, Django will automatically include your site settings in the context.

### Summary

- **Context processors** allow you to define variables globally for all templates.
- They help reduce redundancy by avoiding the need to pass common data in every view.
- They are configured in `settings.py` under the `TEMPLATES` setting.
- You can also create custom context processors for application-specific needs.

Context processors are a powerful tool for maintaining clean, DRY (Don't Repeat Yourself) code in your Django projects.