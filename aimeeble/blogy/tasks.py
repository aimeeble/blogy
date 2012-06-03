from celery.task import task
from blogy.models import Entry
from blogy.models import Tag
from blogy.process import get_static_filename
from blogy.process import generate_static_content
from blogy.process import generate_static_index
from blogy.process import generate_static_tag_index
from django.utils import timezone
import os


@task(ignore_results=True)
def process_pending_posts_task():
   """Task to process next post.

   This will be run in time for processing the next pending post.  Processing
   will use the same code as post_save_handler, which is used for non
   post-dated posts.
   """
   print "Processing..."
   now = timezone.now()
   entries = Entry.objects.filter(post__lte=now)
   for entry in entries:
      filename = get_static_filename(entry)
      if not os.path.exists(filename):
         print "processing '%s'" % (entry.slug)
         generate_static_content(entry)


@task(ignore_results=True)
def generate_main_index_task():
   """Task to re-generate the main index.

   """
   print "Generating indexes..."
   generate_static_index()


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
      generate_static_tag_index(tag)
