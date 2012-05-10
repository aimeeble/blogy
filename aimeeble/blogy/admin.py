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
   list_display = ("title", "is_future_post")
   prepopulated_fields = {
         "slug": ["title"],
      }

   def formfield_for_foreignkey(self, db_field, request, **kwargs):
      if db_field.name == 'posted_by':
         kwargs["initial"] = request.user.id
         return db_field.formfield(**kwargs)
      return super(EntryAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

admin.site.register(Entry, EntryAdmin)
admin.site.register(Tag)
