from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm
)
from django.http import HttpResponseRedirect


User = get_user_model()


class Top(generic.TemplateView):
    template_name = 'register/top.html'


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'register/logout.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('register/mail_template/create/subject.txt', context)
        message = render_to_string('register/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('register:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'register/user_detail.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く


class UserUpdate(OnlyYouMixin, generic.UpdateView,generic.edit.ModelFormMixin):
    """ユーザー情報更新ページ"""
    model = User
    template_name = 'register/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く
    form_class = UserUpdateForm

    def get_success_url(self):
        return resolve_url('register:top')

"""  print('outside')
    def get_context_data(self, **kwargs):
        # スーパークラスのget_context_dataを使うとobject_listに
        # 表示中のモデルの情報が入るのでそれを利用
        context = super().get_context_data(**kwargs)
        # contextは辞書型
        context.update({
            'user_update_form': UserUpdateForm(**self.get_form_kwargs()),
            'email_change_form': EmailChangeForm(**self.get_form_kwargs()),
        })
        return context

    def form_valid(self,form):
        return HttpResponseRedirect('/')
    
    def post(self, request, *args, **kwargs):
        # 質問文変更ボタンがPOSTにあるとき
        print('inside')
        print(request.POST)
        if 'user_update_form' in request.POST:
            qform = UserUpdateForm(**self.get_form_kwargs())
            # バリデーション
            print('inside')
            if qform.is_valid():
                # フォームに書き込んだ部分を取得する(保存しない)
                qform.save()
                qform_query.pk=User.objects.get(pk=self.kwargs['pk'])
                # 保存
                #qform_query.save()
                return HttpResponseRedirect('/user/update/done')
            else:
                self.object = self.get_object()
                return self.form_invalid()
        # 選択肢の文変更ボタンがPOSTにあるとき
        elif 'email_change_form' in request.POST:
            cform = forms.EmailChangeForm(**self.get_form_kwargs())
            # バリデーション
            if cform.is_valid():
                # フォームに書き込んだ部分を取得する(保存しない)
                cform_query = cform.save(commit=False)
                cform_query.pk=User.objects.get(pk=self.kwargs['pk'])
                # 保存
                #cform_query.save()
                return self.form_valid()
            else:
                self.object = self.get_object()
                return self.form_invalid()"""

                


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('register:password_change_done')
    template_name = 'register/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'register/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'register/mail_template/password_reset/subject.txt'
    email_template_name = 'register/mail_template/password_reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('register:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'register/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'register/password_reset_complete.html'


class EmailChange(LoginRequiredMixin, generic.FormView):
    """メールアドレスの変更"""
    template_name = 'register/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('register/mail_template/email_change/subject.txt', context)
        message = render_to_string('register/mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('register:email_change_done')


class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    """メールアドレスの変更メールを送ったよ"""
    template_name = 'register/email_change_done.html'


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """リンクを踏んだ後に呼ばれるメアド変更ビュー"""
    template_name = 'register/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)


from django import forms
import requests
from .parsejson import parse_json_response
from .forms import OCRForm
from .models import Diary,User

class OCR(generic.FormView):
    model = Diary
    form_class = OCRForm
    template_name = 'register/Img_To_Note.html'

    def form_valid(self, form):
        response_str = form.read_str()
        print(self.request.POST)
        if 'convert' in self.request.POST:
            print(1)
            context = {
                'response_str': response_str,
                'form': form,
            }
            return self.render_to_response(context)

        if 'create' in self.request.POST:
            print(2)
            model.created_by = self.request.user
            model.title = timezone.now()
            model.text = response_str
            model.save()
            return redirect('register:list')

        

from django.views import generic



class ArchiveListMixin:
    model = Diary
    paginate_by = 12
    date_field = 'created_at'
    template_name = 'register/diary_list.html'
    allow_empty = True
    make_object_list = True

class ArchiveListMixin:
    model = Diary
    paginate_by = 12
    date_field = 'created_at'
    template_name = 'register/diary_list.html'
    allow_empty = True
    make_object_list = True

from django.db.models import F,Q
class DiaryList(ArchiveListMixin, generic.ArchiveIndexView):

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'User':User
        })
        context['heading'] = 'Your Notes'
        return context
    def get_queryset(self):
        id = self.request.user.id
        q_word = self.request.GET.get('query')

        if q_word:
            object_list = Diary.objects.filter(
                Q(title__icontains=q_word) | Q(text__icontains=q_word))
        else:
            object_list = Diary.objects.all()

        return object_list.get_queryset().filter(created_by = id)



# 追加
from django.http import Http404
from django.utils import timezone

from .forms import DiaryForm
# 追加
class DiaryDetail(generic.DetailView):
    model = Diary
    form_class = DiaryForm

    def get_object(self, queryset=None):
        diary = super().get_object()
        if diary.created_at <= timezone.now():
            return diary
        raise Http404


from django.shortcuts import render,redirect # redirectを追記
from django.http import Http404
from . import models

from django.views.generic.edit import UpdateView

# 略


"""class DiaryEdit(generic.UpdateView):
    model = Diary
    field = '__all__'
    success_url = redirect('list')
    def edit(request,pk):
        template_name = "register/edit.html"
        
        if request.method == "POST":
            Diary.title = request.POST["title"]
            Diary.text = request.POST["text"]
            Diary.save()
            return redirect('list')
        context = {"title": diary.title,
                    "text":diary.text}
        return render(request, template_name, context)"""


class DiaryCreate(generic.CreateView):
    model = Diary
    template_name = "register/create.html"
    form_class = DiaryForm
    success_url = reverse_lazy('register:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user

        diary= form.save()

        # 保存してもう一つ追加ボタンのとき
        if 'save_and_add' in self.request.POST:
            return redirect('register:create')

        # 保存して編集を続けるボタン
        elif 'save_and_edit' in self.request.POST:
            return redirect('register:edit', pk=post.pk)

        return redirect('register:list')

class DiaryEdit(generic.UpdateView):
    model = Diary
    field = '__all__'
    form_class = DiaryForm
    template_name = "register/edit.html"
    success_url = reverse_lazy('register:list')
    def form_valid(self,form):
        diary= form.save()
        

        # 保存してもう一つ追加ボタンのとき
        if 'save_and_add' in self.request.POST:
            return redirect('register:create')

        # 保存して編集を続けるボタン
        elif 'save_and_edit' in self.request.POST:
            return redirect('register:update', pk=post.pk)

        return redirect('register:list')


class Diary_created(generic.CreateView):
    model = Diary
    template_name = "register/create.html"
    form_class = DiaryForm
    success_url = reverse_lazy('register:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user

        diary= form.save()

        # 保存してもう一つ追加ボタンのとき
        if 'save_and_add' in self.request.POST:
            return redirect('register:create')

        # 保存して編集を続けるボタン
        elif 'save_and_edit' in self.request.POST:
            return redirect('register:edit', pk=post.pk)

        return redirect('register:list')