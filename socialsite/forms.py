from django import forms;
from django.contrib.auth.models import User;
from socialsite.models import UserProfile;

class UserForm(forms.ModelForm):
	username = forms.CharField(help_text = "Username:");
	password = forms.CharField(help_text = "Password:", widget = forms.PasswordInput());
	email = forms.CharField(help_text = "Email:");

	class Meta:
		model = User;
		fields = ["username", "email", "password"];



class UserProfileRegisterForm(forms.ModelForm):
	error_css_class = "errorlist";
	required_css_class = "errorlist";
	first_name = forms.CharField(help_text = "First Name:");
	middle_name = forms.CharField(help_text = "Middle Name (optional):", required = False);
	last_name = forms.CharField(help_text = "Last Name (optional):", required = False);
	
	class Meta:
		model = UserProfile;
		fields = ["first_name", "middle_name", "last_name"];



class UserProfileSettingsForm(forms.ModelForm):
	error_css_class = "errorlist";
	required_css_class = "errorlist";
	first_name = forms.CharField(help_text = "First Name:", max_length = 256);
	middle_name = forms.CharField(help_text = "Middle Name (optional):", required = False, max_length = 256);
	last_name = forms.CharField(help_text = "Last Name (optional):", required = False, max_length = 256);
	description = forms.CharField(widget = forms.Textarea(attrs = {"maxlength": 256}), help_text = "About you:", required = False, max_length = 256);
	website = forms.CharField(help_text = "Your website (optional):", required = False, max_length = 256);
	profile_image = forms.ImageField(help_text = "PROFILE_IMAGE", required = False);



	def clean(self):
		cleanedData = self.cleaned_data;
		website = cleanedData.get("website");

		if (website):
			if (not website.startswith("http://") and not website.startswith("https://")):
				website = "http://" + website;

			if (not website.endswith("/")):
				website += "/";

			cleanedData["website"] = website;

		return cleanedData;



	class Meta:
		model = UserProfile;
		fields = ["first_name", "middle_name", "last_name", "description", "website", "profile_image"];