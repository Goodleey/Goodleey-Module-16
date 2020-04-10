from django import forms  
from allauth.socialaccount.models import SocialAccount
from p_library.models import Author, Book, Friend, UserProfile
  
class AuthorForm(forms.ModelForm):

    full_name = forms.CharField(widget=forms.TextInput)

    class Meta:  
        model = Author  
        fields = '__all__'


class BookForm(forms.ModelForm):  
    class Meta:  
        model = Book  
        fields = '__all__'


class FriendForm(forms.ModelForm):  

    name = forms.CharField(widget=forms.TextInput)

    class Meta:  
        model = Friend  
        fields = '__all__'


class ProfileCreationForm(forms.ModelForm):  
  
    age = forms.IntegerField()

    class Meta:  
        model = UserProfile
        fields = []