from blogy.models import Entry
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.db.models.signals import m2m_changed
from blogy.tasks import process_pending_posts_task
from blogy.tasks import generate_main_index_task
from blogy.tasks import generate_tag_index_task
from blogy.process import cleanup_static_content
from blogy.process import delete_static_file


@receiver(post_save, sender=Entry)
def entry_post_save_handler(sender, instance, **kwargs):
   # Handle this asyncly via a Celery task
   process_pending_posts_task.delay()
   generate_main_index_task.delay()


@receiver(pre_save, sender=Entry)
def entry_pre_save_handler(sender, instance, **kwargs):
   cleanup_static_content(instance)


@receiver(pre_delete, sender=Entry)
def entry_delete_handler(sender, instance, **kwargs):
   delete_static_file(instance)
   generate_main_index_task.delay()
   tags = map(lambda x: x.name, instance.tags.all())
   generate_tag_index_task.delay(tags)


@receiver(m2m_changed, sender=Entry.tags.through)
def tag_post_save_handler(sender, instance, action, **kwargs):
   if action == "post_add":
      tags = map(lambda x: x.name, instance.tags.all())
      if tags:
         generate_tag_index_task.delay(tags)
   elif action == "pre_clear":
      tags = map(lambda x: x.name, instance.tags.all())
      if tags:
         generate_tag_index_task.delay(tags)
