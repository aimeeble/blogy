from blogy.models import Entry
from blogy.models import Tag
from django.conf import settings
from django.template import Context
from django.template import loader
from django.utils import timezone
from markdown import Markdown
import os
import errno
from django.template.defaultfilters import slugify


def _ensure_path(path):
   try:
      os.makedirs(path)
   except OSError, e:
      if e.errno != errno.EEXIST:
         raise e


class StaticEntry(object):
   def __init__(self, entry):
      self.entry = entry

   def _get_symlink_name(self):
      """Gets the symlink filename for this entry.

      """
      posted = timezone.localtime(self.entry.post)

      filename = "%s.html" % (self.entry.slug)
      path = os.path.join(settings.MEDIA_ROOT,
                              "blog",
                              "%4u" % (posted.year),
                              "%02u" % (posted.month))
      abs_filename = os.path.join(path, filename)
      return abs_filename

   def _get_html_name(self):
      """Gets the actual HTML filename for this entry.

      """
      filename = "%s.html" % (self.entry.guid)
      path = os.path.join(settings.MEDIA_ROOT,
                          "blog",
                          "posts")
      abs_filename = os.path.join(path, filename)
      return abs_filename

   def delete_html(self):
      filename = self._get_html_name()
      try:
         os.unlink(filename)
      except OSError, e:
         if e.errno == errno.ENOENT:
            print "failure: %s" % (str(e))
         else:
            raise e

   def delete_symlink(self):
      filename = self._get_symlink_name()
      try:
         os.unlink(filename)
      except OSError, e:
         if e.errno == errno.ENOENT:
            print "failure: %s" % (str(e))
         else:
            raise e

   def generate_html(self):
      """Generate the static HTML file for an entry.

      This will create the static HTML file which represents the post itself.
      The entry's markdown source is converted into HTML and sandwiched with
      the template head/foot then saved to a URL based upon the entry's slug.

      """
      filename = self._get_html_name()

      if os.path.exists(filename):
         print "Already done %s" % filename
         return

      print "Generating %s" % (filename)
      _ensure_path(os.path.dirname(filename))

      md = Markdown(["abbr", "def_list"])
      post_html = md.convert(self.entry.markdown)
      post_tags = map(lambda x: x.name, self.entry.tags.all())

      t = loader.get_template("entry.html")
      c = Context({
         "post_title": self.entry.title,
         "post_body": post_html,
         "post_tags": post_tags,
         "post_date": self.entry.post,
      })
      full_html = t.render(c)

      with open(filename, "w+") as f:
         f.write(full_html)

   def symlink(self):
      """This will symlink the post into place.

      Note that this only creates a symlink if both finished=True and
      now>posted.

      """
      if not self.entry.finished:
         print "not symlinking for unfinished post on %s" % (str(self.entry.slug))
         return

      html_name = self._get_html_name()
      html_name = os.path.abspath(html_name)
      link_name = self._get_symlink_name()

      _ensure_path(os.path.dirname(link_name))

      print "Symlinking %s to %s" % (link_name, html_name)
      try:
         os.symlink(html_name, link_name)
      except OSError, e:
         if e.errno == errno.EEXIST:
            print "failure: %s" % (str(e))
         else:
            raise e


class StaticIndex(object):
   def __init__(self, tagname=None):
      now = timezone.now()

      if tagname:
         self.entries = Entry.objects.filter(finished=True, post__lte=now, tags__name=tagname).order_by("-post")
         slugged_tagname = slugify(tagname)
         self.filename = os.path.join("tags", "%s.html" % slugged_tagname)
      else:
         self.entries = Entry.objects.filter(finished=True, post__lte=now).order_by("-post")
         self.filename = "index.html"

   def _get_html_name(self):
      """Gets the HTML filename for this index.

      """
      return os.path.join(settings.MEDIA_ROOT, "blog", self.filename)

   def generate_html(self):
      filename = self._get_html_name()
      print "Generating %s" % (filename)

      tags = Tag.objects.all()

      t = loader.get_template("index.html")
      c = Context({
         "entry_list": self.entries,
         "tags": tags,
      })
      full_html = t.render(c)

      _ensure_path(os.path.dirname(filename))
      with open(filename, "w+") as f:
         f.write(full_html)
