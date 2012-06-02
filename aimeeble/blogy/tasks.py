from celery.task import task
from blogy.models import Entry
from blogy.process import get_static_filename
from blogy.process import generate_static_content
from blogy.process import generate_static_index
from django.utils import timezone
import os


@task
def process_pending_posts():
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
         generate_static_index()
