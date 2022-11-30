from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User
from instagram.forms import PostForm, CommentForm
from instagram.models import Post, Comment


@login_required
def index(request):
    post_list = Post.objects.all() \
        .filter(
        Q(author=request.user) |
        Q(author__in=request.user.following_set.all())
    )

    comment_form = CommentForm()

    suggested_user_list = get_user_model().objects.all() \
        .exclude(pk=request.user.pk) \
        .exclude(pk__in=request.user.following_set.all())
    return render(request, 'instagram/index.html', {
        'post_list': post_list,
        'suggested_user_list': suggested_user_list,
        'comment_form': comment_form,
    })


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post.tag_set.add(*post.extract_tag_list())
            post.caption_replace()
            post.save()
            messages.success(request, '새 포스팅을 생성하였습니다.')
            return redirect('root')
    else:
        form = PostForm()
    return render(request, 'instagram/post_form.html', {
        'form': form
    })


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm()
    return render(request, 'instagram/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
    })


@login_required
def user_page(request, username):
    page_user = get_object_or_404(User, username=username, is_active=True)
    post_list = Post.objects.filter(author=page_user)
    post_list_count = post_list.count()

    follower_count = page_user.follower_set.count()
    following_count = page_user.following_set.count()

    if request.user.is_authenticated:
        is_follow = page_user.follower_set.filter(pk=request.user.pk).exists()
    else:
        is_follow = False

    return render(request, 'instagram/user_page.html', {
        'page_user': page_user,
        'post_list': post_list,
        'post_list_count': post_list_count,

        'is_follow': is_follow,
        'follower_count': follower_count,
        'following_count': following_count,

    })


@login_required
def comment_new(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return render(request, 'instagram/_comment.html', {
                    'comment': comment,
                })
            return redirect(comment.post)
    else:
        form = CommentForm()
    return render(request, 'instagram/comment_form.html', {
        'form': form,
    })


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.add(request.user)
    messages.success(request, f'{post.pk}번 게시물을 좋아요 하였습니다.')
    redirect_url = request.META.get('HTTP_REFERER', 'root')
    return redirect(redirect_url)


@login_required
def post_unlike(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.like_user_set.remove(request.user)
    messages.success(request, f'{post.pk}번 게시물을 좋아요 취소하였습니다.')
    redirect_url = request.META.get('HTTP_REFERER', 'root')
    return redirect(redirect_url)