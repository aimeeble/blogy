from blogy.models import Tag
from blogy.models import Entry
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
   readonly_fields = ["created", "modified"]
   fieldsets = [
         ("Dates", {
            "fields": ["created", "modified", "post"],
            "classes": ["collapse"],
         }),
         ("Content", {
            "fields": ["title", "markdown"],
         }),
         ("Misc", {
            "fields": ["slug", "posted_by", "tags"],
            "classes": ["collapse"],
         }),
      ]
   list_display = ("title", "posted", "modified", "posted_by", "get_tags")
   prepopulated_fields = {
         "slug": ["title"],
      }

   def formfield_for_foreignkey(self, db_field, request, **kwargs):
      """Defaults posted-by field to the logged in user.

      Pre-populates the foreign-key field for posted-by to be set to the
      currently logged in user.

      """
      if db_field.name == 'posted_by':
         kwargs["initial"] = request.user.id
         return db_field.formfield(**kwargs)
      return super(EntryAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

admin.site.register(Entry, EntryAdmin)
admin.site.register(Tag)
