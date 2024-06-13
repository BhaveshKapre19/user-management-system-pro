from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUserModel , UserFiles

from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    avatar = forms.FileField(required=False)
    
    class Meta(UserCreationForm.Meta):
        model = CustomUserModel
        fields = ('username', 'email', 'password1', 'password2', 'avatar')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUserModel
        fields = ['email', 'password']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUserModel
        fields = ['username', 'email', 'bio', 'avatar']


class UserFileForm(forms.ModelForm):
    class Meta:
        model = UserFiles
        fields = ['file']



class ShareFileForm(forms.Form):
    recipient = forms.CharField(label='Email or Username')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the current user
        super().__init__(*args, **kwargs)

    def clean_recipient(self):
        username_or_email = self.cleaned_data['recipient']
        try:
            recipient_user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                recipient_user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid username or email.')

        if recipient_user == self.user:
            raise forms.ValidationError('You cannot share files with yourself.')

        return recipient_user