from django.contrib import admin
from django_gitweb.repositories.models import Member, Repository
from django_gitweb.repositories.forms import RepositoryForm

class MemberInline(admin.TabularInline):
    model = Member
    extra = 2

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_public', 'path')
    save_on_top = True
    form = RepositoryForm
    inlines = (MemberInline,)

admin.site.register(Repository, RepositoryAdmin)

