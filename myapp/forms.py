from django import forms

class RegisterForm(forms.Form):
    fullname = forms.CharField(max_length=200, label="Full Name")
    email = forms.EmailField(label="CIT Email")
    id_no = forms.CharField(max_length=150, label="ID Number")
    role = forms.ChoiceField(
        choices=[("security", "Security Officer"), ("supervisor", "Supervisor"), ("admin", "Administrator")],
        label="Role"
    )
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not email.lower().endswith("@cit.edu"):
            raise forms.ValidationError("Email must be a valid @cit.edu address")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
