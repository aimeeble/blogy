from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template import Context
from django.template import loader
from django.utils import timezone

from blogy.models import Entry
from markdown import Markdown
import os


def get_static_filename(entry):
   """Gets the absolute filename of the entry's static HTML file.

   """
   posted = timezone.localtime(entry.post)

   filename = "%s.html" % (entry.slug)
   path = os.path.join(settings.MEDIA_ROOT,
                           "blog",
                           "%4u" % (posted.year),
                           "%02u" % (posted.month),
                           "%02u" % (posted.day))
   abs_filename = os.path.join(path, filename)

   try:
      os.makedirs(path)
   except OSError, e:
      pass

   return abs_filename


def delete_static_file(entry):
   """Delete the HTML file associated with entry.

   """
   abs_filename = get_static_filename(entry)

   print "Unlinking %s" % (abs_filename)
   try:
      os.unlink(abs_filename)
   except OSError, e:
      print "failure: %s" % (str(e))


@receiver(pre_save, sender=Entry)
def pre_save_handler(sender, instance, **kwargs):
   """Cleans up generated files pre-save.

   Pre-save, we delete the static HTML file if it already exists.  This does
   two main things, 1) if the slug changes, this ensures the old file is
   removed before we re-generate into the new slug file, and 2) handles hiding
   a HTML file if the post-date has been changed to be in the future (invisible
   until the date specified).

   """
   if not instance.id:
      return
   old = Entry.objects.get(pk=instance.id)
   delete_static_file(old)


@receiver(post_save, sender=Entry)
def post_save_handler(sender, instance, **kwargs):
   """Generate the static HTML file for an entry.

   After the bookkeeping data is saved to the database, this will create the
   static HTML file which represents the post itself.  The instance's markdown
   source is converted into HTML and sandwiched with the template head/foot
   then saved to a URL based upon the instance's slug.

   """
   if not instance.posted():
      print "not generating for future post on %s" % (str(instance.post))
      return

   md = Markdown()
   post_html = md.convert(instance.markdown)

   t = loader.get_template("blogy/entry.html")
   c = Context({
      "post_title": instance.title,
      "post_body": post_html,
   })
   full_html = t.render(c)

   abs_filename = get_static_filename(instance)

   with open(abs_filename, "w+") as f:
      f.write(full_html)
   print "saving %s to %s ->\n%s" % (instance.title, abs_filename, full_html)


@receiver(pre_delete, sender=Entry)
def delete_handler(sender, instance, **kwargs):
   """Cleanup static HTML for a deleted post.

   Before we remove our bookkeeping data, delete the static file.  Should the
   delete fail, re-saving we re-generate the file we delete here.

   """
   delete_static_file(instance)


def setup_signals():
   pass
