from django.views.generic import ListView, FormView
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from articles.model_forms import CommentModelForm
from articles.models import Article, Like, Comment
from django.urls import reverse_lazy
from django.http import Http404


class ArticleView(ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'articles/index.html'


class ArticleDetailView(FormView):
    form_class = CommentModelForm
    template_name = 'articles/detail.html'
    success_url = reverse_lazy('articles')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.article = Article.objects.get(slug=kwargs.get('slug'))
        except Article.DoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['article'] = self.article
        context['likes'] = Like.objects.filter(article=self.article,
                                               is_like=True).count()
        context['dislikes'] = Like.objects.filter(article=self.article,
                                               is_like=False).count()
        context['comments'] = Comment.objects.filter(article=self.article)
        if self.request.user.is_anonymous:
            kwargs.pop('form')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'article': self.article
        })
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('article_details',
                            kwargs={'slug': self.article.slug})


class LikeOrDislikeArticleView(RedirectView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            self.article = Article.objects.get(slug=kwargs.get('slug'))
        except Article.DoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('article_details',
                            kwargs={'slug': self.article.slug})

    def post(self, request, *args, **kwargs):
        action = kwargs.get('action')
        like, created = Like.objects.get_or_create(
            article=self.article,
            user=self.request.user
        )
        if action == 'like':
            if not created and like.is_like:
                like.delete()
            if not created and not like.is_like:
                like.is_like = True
                like.save()
        if action == 'dislike':
            if not created and not like.is_like:
                like.delete()
            if not created and like.is_like:
                like.is_like = False
                like.save()
            if created:
                like.is_like = False
                like.save()
        return self.get(request, *args, **kwargs)
