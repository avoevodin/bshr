"""
Common utilities for service communicates.
"""


async def send_register_confirmation_message(user_in):
    """
    Send register confirmation message for the new user.

    Returns:

    """
    # Temporary send only email.
    # if settings.EMAILS_ENABLED and user_in.email:
    #     send_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
