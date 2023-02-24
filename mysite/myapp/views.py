import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404

from .forms import InquiryForm, MyappCreateForm
from .models import Myapp

logger = logging.getLogger(__name__)

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # URLに埋め込まれた主キーから日記データを1件取得。取得できなかった場合は404エラー
        myapp = get_object_or_404(Myapp, pk=self.kwargs['pk'])
        # ログインユーザーと日記の作成ユーザーを比較し、異なればraise_exceptionの設定に従う
        return self.request.user == myapp.user

class IndexView(generic.TemplateView):
    template_name = "index.html"

class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('myapp:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)

class MyappListView(LoginRequiredMixin, generic.ListView):
    model = Myapp
    template_name = 'myapp_list.html'
    paginate_by = 2

    def get_queryset(self):
        diaries = Myapp.objects.filter(user=self.request.user).order_by('-created_at')
        return diaries

class MyappDetailView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Myapp
    template_name = 'myapp_detail.html'

class MyappCreateView(LoginRequiredMixin, generic.CreateView):
    model = Myapp
    template_name = 'myapp_create.html'
    form_class = MyappCreateForm
    success_url = reverse_lazy('myapp:myapp_list')

    def form_valid(self, form):
        myapp = form.save(commit=False)
        myapp.user = self.request.user
        myapp.save()
        messages.success(self.request, '日記を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "日記の作成に失敗しました。")
        return super().form_invalid(form)

class MyappUpdateView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):
    model = Myapp
    template_name = 'myapp_update.html'
    form_class = MyappCreateForm

    def get_success_url(self):
        return reverse_lazy('myapp:myapp_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "日記の更新に失敗しました。")
        return super().form_invalid(form)

class MyappDeleteView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):
    model = Myapp
    template_name = 'myapp_delete.html'
    success_url = reverse_lazy('myapp:myapp_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "日記を削除しました。")
        return super().delete(request, *args, **kwargs)