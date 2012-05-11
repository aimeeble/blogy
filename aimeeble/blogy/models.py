from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify

# Create your models here.

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
   markdown = models.TextField()

   # when
   created = models.DateTimeField('Date created', auto_now_add=True)
   modified = models.DateTimeField('Last Modified Date', auto_now=True)
   post = models.DateTimeField('Post Date', default=timezone.now)

   # who
   posted_by = models.ForeignKey(User)

   # random tags we are tagged with
   tags = models.ManyToManyField('Tag', blank=True)

   def posted(self):
      """Returns true if this has been posted (false = future post).
      """
      return self.post <= timezone.now()
   posted.admin_order_field = 'post'
   posted.boolean = True
   posted.short_description = 'Posted'

   def get_tags(self):
      """Returns a comma-separated list of tags for this post.
      """
      return ", ".join([t.name for t in self.tags.all()])
   get_tags.short_description = 'Tags'

   def __unicode__(self):
      return "%s (post %s)" % (self.title, str(self.post))

