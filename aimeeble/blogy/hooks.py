from blogy.models import Entry
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from blogy.tasks import process_pending_posts

from blogy.process import generate_static_index
from blogy.process import cleanup_static_content
from blogy.process import delete_static_file


@receiver(post_save, sender=Entry)
def post_save_handler(sender, instance, **kwargs):
   # Handle this asyncly via a Celery task
   process_pending_posts.delay()


@receiver(pre_save, sender=Entry)
def pre_save_handler(sender, instance, **kwargs):
   cleanup_static_content(instance)


@receiver(pre_delete, sender=Entry)
def delete_handler(sender, instance, **kwargs):
   delete_static_file(instance)
   generate_static_index()
