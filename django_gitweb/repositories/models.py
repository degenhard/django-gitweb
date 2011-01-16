from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.defaultfilters import slugify
import os
from dulwich import repo

REPOSITORY_PUBLIC_FILTER = lambda u: Q(is_public=True)
REPOSITORY_LOGGED_IN_FILTER = lambda u: Q(
    Q(is_public=True) | Q(member__user=u)
)

class RepositoryManager(models.Manager):
    def visible_repositories_for_user(self, user=None):
        if not user or not user.is_authenticated():
            qset = REPOSITORY_PUBLIC_FILTER(user)
        else:
            qset = REPOSITORY_LOGGED_IN_FILTER(user)

        return self.get_query_set().filter(qset)

class Repository(models.Model):
    path = models.CharField(_('Repository Path'), max_length=255)
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, blank=False)
    description = models.TextField(_('Description'), blank=True)
    is_public = models.BooleanField(_('Is Public'), default=False)

    objects = RepositoryManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(os.path.split(self.path)[-1])
        super(Repository, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def get_absolute_tree_url(self):
        return reverse(viewname='gitweb_repository_tree',
                       kwargs={'id': self.pk,
                               'slug': self.slug,
                               'branch': self.active_branch})

    """
    def get_absolute_commits_url(self):
        return reverse(viewname='gitweb_repository_commits',
                       kwargs={'project_name': self.slug,
                               'hash_name': self.active_branch()})
    """

    def get_absolute_url(self):
        return self.get_absolute_tree_url()

    def repo(self):
        return repo.Repo(self.path)

    def branches(self):
        branches = self.repo().branches
        return branches

    @property
    def active_branch(self):
        return self.repo().active_branch

    @property
    def tags(self):
        return self.repo().tags

    @property
    def recent_commits(self):
        return self.repo().commits(
            max_count=getattr(settings, 'GITWEB_RECENT_COMMITS_COUNT', 10))

    @property
    def last_commit(self):
        return self.repo().head

    @property
    def last_commit_object(self):
        return self.repo().commit(self.repo().head())

    class Meta:
        verbose_name = _('Repository')
        verbose_name_plural = _('Repositories')

class Member(models.Model):
    repository = models.ForeignKey(Repository, verbose_name=_('Repository'))
    user = models.ForeignKey(User, verbose_name=_('User'))
    can_download = models.BooleanField(_('Can download'), default=True)
    can_view_content = models.BooleanField(_('Can view content'), default=True)

    def __unicode__(self):
        return '%s: %s' % (self.repository, self.user)

    class Meta:
        unique_together = ('repository', 'user')
        verbose_name = _('Repository User')
        verbose_name_plural = _('Repository Users')

