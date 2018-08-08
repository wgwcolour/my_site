from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Comment
"""用户注册"""
class RegisterForm(forms.Form):
	email = forms.EmailField()
	passwd = forms.CharField(max_length=20)
"""class UserRegisterForm(UserCreationForm):
	class Meta(UserCreationForm):
		model = User
"""
"""用户登录"""
class LoginForm(forms.Form):
	email = forms.EmailField()
	passwd = forms.CharField(max_length=20)
'''发表评论'''
class CommentForm(forms.ModelForm):
	class Meta():
		model = Comment
		fields = ["body"]