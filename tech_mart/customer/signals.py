from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer
from .helper import MessageHandler


@receiver(post_save, sender=Customer)
def otp_sending(sender, instance, created, update_fields, **kwargs):
    try:
        if created or "otp" in update_fields:
            print(instance.phone_number)
            MessageHandler(instance.phone_number, instance.otp).send_otp_via_message()
    except Exception as e:
        print(e)
