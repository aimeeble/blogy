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

   def save(self, *args, **kwargs):
      self.slug = slugify(self.title)
      super(Entry, self).save(*args, **kwargs)

   def is_future_post(self):
      return self.post > timezone.now()

   def __unicode__(self):
      return "%s (post %s)" % (self.title, str(self.post))

