from blogy.models import Entry
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.db.models.signals import m2m_changed
from blogy.tasks import generate_main_index_task
from blogy.tasks import generate_tag_index_task
from blogy.process import StaticEntry


@receiver(pre_save, sender=Entry)
def entry_pre_save_handler(sender, instance, **kwargs):
   # serach for ourself--we want to refer to old names in the event they have
   # been changed in the instance object we were given.
   if instance.id:
      old = Entry.objects.get(pk=instance.id)
      old_static_entry = StaticEntry(old)

      if instance.slug != old.slug or not instance.finished:
         old_static_entry.delete_symlink()
      if instance.markdown != old.markdown:
         print "content changed, flagging for re-render"
         instance.rendered = False


@receiver(pre_delete, sender=Entry)
def entry_delete_handler(sender, instance, **kwargs):
   static_entry = StaticEntry(instance)
   static_entry.delete_symlink()
   static_entry.delete_html()

   # and now the indexes
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
