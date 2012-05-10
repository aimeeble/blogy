from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template import Context
from django.template import loader

from blogy.models import Entry
from markdown import Markdown
import os

@receiver(post_save, sender=Entry)
def save_handler(sender, instance, **kwargs):
   """Generate the static HTML file for an entry.

   After the bookkeeping data is saved to the database, this will create the
   static HTML file which represents the post itself.  The instance's markdown
   source is converted into HTML and sandwiched with the template head/foot
   then saved to a URL based upon the instance's slug.

   """
   md = Markdown()
   post_html = md.convert(instance.markdown)

   t = loader.get_template("blogy/entry.html")
   c = Context({
      "post_title": instance.title,
      "post_body": post_html,
   })
   full_html = t.render(c)

   filename = "%s.html" % (instance.slug)
   path = os.path.join(settings.MEDIA_ROOT,
                           "blog",
                           "%4u" % (instance.post.year),
                           "%02u" % (instance.post.month),
                           "%02u" % (instance.post.day))
   abs_filename = os.path.join(path, filename)

   try:
      os.makedirs(path)
   except OSError, e:
      pass
   with open(abs_filename, "w+") as f:
      f.write(full_html)
   print "saving %s to %s ->\n%s" % (instance.title, abs_filename, full_html)

@receiver(pre_delete, sender=Entry)
def delete_handler(sender, instance, **kwargs):
   """Cleanup static HTML for a deleted post.

   Before we remove our bookkeeping data, delete the static file.  Should the
   delete fail, re-saving we re-generate the file we delete here.

   """
   print "deleting %s" % (instance.title)


def setup_signals():
   pass
