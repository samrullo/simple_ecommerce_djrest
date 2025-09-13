# How to customize email confirmation message body

By defining following files in <root>/templates/account/email

Also following class allows to define variables like ```activate_url``` within message body
When registering new user I am inherit from ```from dj_rest_auth.registration.views import RegisterView```

```python
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailConfirmation

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        logger.debug("CustomAccountAdapter.save_user() called")
        # First let the parent adapter save the user (this handles basic fields)
        logging.debug(f"commit is {commit}")
        user = super().save_user(request, user, form, commit=True)

        # Ensure the user is saved (has a primary key) before creating related objects.
        if not user.pk:
            user.save()
            logger.debug("User saved to ensure it has a primary key.")

        # Now, access your custom fields from the form's cleaned_data.
        # Note: If you’re using a custom serializer, you may need to pass these values
        # differently; adjust accordingly.
        extra_data = form.cleaned_data
        customer_data = extra_data.get("customer")
        address_data = extra_data.get("address")
        logger.debug(f"customer data : {customer_data}, address_data : {address_data}")

        if customer_data:
            # Create your Customer instance
            Customer.objects.create(user=user, **customer_data)
            logger.debug("Customer created with: %s", customer_data)
        if address_data:
            # You might need to first ensure the customer exists
            customer = getattr(user, "customer", None)
            if customer:
                Address.objects.create(customer=customer, **address_data)
                logger.debug("Address created with: %s", address_data)

        return user

    def send_confirmation_mail(
            self, request, emailconfirmation: EmailConfirmation, signup
    ):
        """
        Override the confirmation link sent in the email.
        """
        logger.debug("CustomAccountAdapter.send_confirmation_mail called")

        # 🔗 Build a link to your React frontend
        react_link = f"http://localhost:3000/verify-email/{emailconfirmation.key}"
        logger.debug(f"Generated react verification link: {react_link}")

        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": react_link,
            "current_site": None,
            "key": emailconfirmation.key,
        }
        self.send_mail(
            "account/email/email_confirmation",
            emailconfirmation.email_address.email,
            ctx,
        )

    # def confirm_email(self, request, email_address):
    #     logger.debug(f"Confirming email for: {email_address.email}")
    #
    #     # ✅ Explicitly mark as verified
    #     email_address.verified = True
    #     email_address.save()
    #
    #     # ✅ Optionally set user on request
    #     request.user = email_address.user
    #     logger.debug(f"Email marked as verified for user: {email_address.user}")

```


Refer to ```custom_user_registration_what_worked.md``` file for more details.