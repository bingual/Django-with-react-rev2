from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView as AuthLoginView, logout_then_login,
                                       PasswordChangeView as AuthPasswordChangeView)
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy

from accounts.forms import SignupForm, ProfileForm, PasswordChangeForm
from django.contrib.auth import login as auth_login, get_user_model

from accounts.models import User


class LoginView(AuthLoginView):
    template_name = 'accounts/login_form.html'

    def get_success_url(self):
        messages.success(self.request, '로그인 되었습니다.')
        return reverse_lazy('root')


login = LoginView.as_view()


@login_required
def logout(request):
    messages.success(request, '로그아웃 되었습니다.')
    return logout_then_login(request)


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            auth_login(request, signed_user)
            messages.success(request, '회원가입을 환영합니다.')
            signed_user.welcome_mail_send()
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup_form.html', {
        'form': form
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필을 수정/저장했습니다.')
            redirect('accounts:profile_edit')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit_form.html', {
        'form': form
    })


class PasswordChangeView(LoginRequiredMixin, AuthPasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('accounts:password_change')
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, '암호를 변경하였습니다.')
        return super().form_valid(form)


password_change = PasswordChangeView.as_view()


def user_follow(request, username):
    following_user = get_object_or_404(get_user_model(), username=username, is_active=True)
    request.user.following_set.add(following_user)
    following_user.follower_set.add(request.user)
    messages.success(request, f'{following_user} 님을 팔로우하였습니다.')
    redirect_url = request.META.get('HTTP_REFERER', 'root')
    return redirect(redirect_url)


def user_unfollow(request, username):
    unfollowing_user = get_object_or_404(get_user_model(), username=username, is_active=True)
    request.user.following_set.remove(unfollowing_user)
    unfollowing_user.follower_set.remove(request.user)
    messages.success(request, f'{unfollowing_user} 님을 언팔로우하였습니다.')
    redirect_url = request.META.get('HTTP_REFERER', 'root')
    return redirect(redirect_url)
