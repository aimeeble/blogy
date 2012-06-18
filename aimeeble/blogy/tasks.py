from celery.task import task
from blogy.models import Entry
from blogy.models import Tag
from blogy.process import StaticEntry
from blogy.process import StaticIndex
from django.utils import timezone
import os


@task(ignore_results=True)
def process_pending_posts_task(entrypk=None):
   """Task to process posts.

   This is where all processing of post markdown to HTML is kicked off from.
   If entrypk is specified, we will only generate that entry.  If it is None,
   we will generate all posts which should but have not yet been processed.
   """
   print "Processing..."

   if entrypk:
      entry = Entry.objects.get(pk=entrypk)
      if not entry:
         raise Exception("invalid pk %s" % entrypk)
      entries = [StaticEntry(entry)]
   else:
      now = timezone.now()
      raw_entries = Entry.objects.filter(finished=True, post__lte=now)
      entries = [StaticEntry(x) for x in raw_entries]

   for entry in entries:
      entry.generate_html()
      entry.symlink()


@task(ignore_results=True)
def generate_main_index_task():
   """Task to re-generate the main index.

   """
   print "Generating indexes..."
   idx = StaticIndex()
   idx.generate_html()


@task(ignore_results=True)
def generate_tag_index_task(tags=None):
   """Task to re-generate tag indexes.

   If tags is specified, only generate indexes for those those tags.
   Otherwise, generate a new index for all tags.
   """
   if not tags:
      tags = map(lambda x: x.name, Tag.objects.all())
   print "Generating indexes for %s..." % (", ".join(tags))

   for tag in tags:
      idx = StaticIndex(tag)
      idx.generate_html()
