from django import forms

from instagram.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['photo', 'caption', 'location']
        widgets = {
            'caption': forms.Textarea,
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['messages']
        widgets = {
            'messages': forms.Textarea(attrs={"rows": 3}),
        }
