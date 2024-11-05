# forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from timer.models import Timer
class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mật khẩu"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nhập lại mật khẩu"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise ValidationError("Mật khẩu và mật khẩu nhập lại không khớp.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Tên người dùng đã tồn tại.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email đã được sử dụng.")
        return email


class TimerForm(forms.ModelForm):
    class Meta:
        model = Timer
        fields = ['device', 'days_of_week', 'start_time', 'end_time', 'is_active']
        widgets = {
            'days_of_week': forms.CheckboxSelectMultiple(),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'device': 'Thiết bị',
            'days_of_week': 'Lặp lại vào các ngày',
            'start_time': 'Giờ bật',
            'end_time': 'Giờ tắt',
            'is_active': 'Trạng thái kích hoạt',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        return cleaned_data