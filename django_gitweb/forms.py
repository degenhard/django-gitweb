from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Repository
from dulwich import repo
import dulwich

class RepositoryForm(forms.ModelForm):
    def clean_path(self):
        try:
            repo.Repo(self.cleaned_data['path'])
        except dulwich.errors.NotGitRepository:
            raise forms.ValidationError(_('Please submit a valid git repository path'))
        except Exception:
            raise forms.ValidationError(_('Please submit a valid file path'))

        return self.cleaned_data['path']

    class Meta:
        model = Repository