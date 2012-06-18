from celery.task import task
from blogy.models import Entry
from blogy.models import Tag
from blogy.process import StaticEntry
from blogy.process import StaticIndex
from django.utils import timezone
import os


@task(ignore_results=True)
def process_pending_posts_task():
   """Task to process pending but not ready entries.

   This will generate all posts which should but have not yet been processed.
   """
   print "Processing pending..."

   now = timezone.now()
   raw_entries = Entry.objects.filter(rendered=False, post__lte=now)
   todo_tags = []

   if not raw_entries:
      print "DEBUG: none pending"
      return

   for entry in raw_entries:
      generate_single_post(entry.id)
      todo_tags += [tag.name for tag in entry.tags.all()]

   generate_main_index_task()
   if todo_tags:
      todo_tags = set(todo_tags)
      generate_tag_index_task(todo_tags)


@task(ignore_results=True)
def generate_single_post(entrypk):
   """Task to process posts.

   This is where all processing of post markdown to HTML is kicked off from.
   """

   raw_entry = Entry.objects.get(pk=entrypk)
   if not raw_entry:
      raise Exception("invalid pk %s" % entrypk)

   if raw_entry.rendered:
      print "DEBUG: skipping previously rendered entry"
      return

   print "rendering entry %s" % (raw_entry.slug)
   entry = StaticEntry(raw_entry)

   # Generate the private guid-based HTML file.
   entry.generate_html()

   # Link the publically visible file only if ready...
   if raw_entry.post <= timezone.now() and raw_entry.finished:
      entry.symlink()

      raw_entry.rendered = True
      raw_entry.save()


@task(ignore_results=True)
def generate_main_index_task():
   """Task to re-generate the main index.

   """
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

   for tag in tags:
      idx = StaticIndex(tag)
      idx.generate_html()
