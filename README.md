blogy
=====

A fairly simple blog system written in Django.  Purpose is primarily for me to
learn the Django framework.

The general idea is posts are written in markdown and the source is stored in
the db.  At the time of posting, they are rendered to a static file based on
the slug.  These will be served up without any db access.
