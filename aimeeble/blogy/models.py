from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify
import uuid


def make_uuid():
   return str(uuid.uuid4())


class Tag(models.Model):
   name = models.CharField(max_length=255)

   def __unicode__(self):
      return "%s" % (self.name)


class Entry(models.Model):
   """A blog entry's metadata.

   The actual reading of the blog is based on a static file.  However, this
   model stores the metadata of a blog post.  It also stores the markdown
   source for editing and re-generating HTML.

   """
   slug = models.SlugField(null=False, unique=True)

   # what
   title = models.CharField(max_length=255)
   markdown = models.TextField(help_text="Entry's main text in Markdown syntax")
   guid = models.TextField(max_length=36, editable=False, default=make_uuid)

   # when
   created = models.DateTimeField('Date created', auto_now_add=True)
   modified = models.DateTimeField('Last Modified Date', auto_now=True)
   post = models.DateTimeField('Post Date', default=timezone.now, help_text="Date on which this entry should be auto-posted (requires finished=True)")

   # If false, no symlink into place; will not appear in index.
   finished = models.BooleanField(default=False, help_text="Is this post finished? If not finished, it is only available privately by GUID.")
   rendered = models.BooleanField(default=False, help_text="internal: Has the post been rendered to HTML yet?")

   # who
   posted_by = models.ForeignKey(User)

   # random tags we are tagged with
   tags = models.ManyToManyField('Tag', blank=True)

   def get_tags(self):
      """Returns a comma-separated list of tags for this post.
      """
      return ", ".join([t.name for t in self.tags.all()])
   get_tags.short_description = 'Tags'

   def __unicode__(self):
      return "%s (post %s)" % (self.title, str(self.post))
