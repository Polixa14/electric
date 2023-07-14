from django import forms
from articles.models import Comment
from django.utils.html import strip_tags


class CommentModelForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('user', 'text', 'article')

    def __init__(self, user, article, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.user = user
        # self.article = article
        # if user:
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].initial = user
        self.fields['article'].widget = forms.HiddenInput()
        self.fields['article'].initial = article

    def clean_text(self):
        text = self.cleaned_data.get('text')
        return strip_tags(text)
