from django import forms
from .models import Contact, Session, Message

class Session_Form(forms.ModelForm):
    class Meta:
        model = Session
        fields = ('phone_number',)

class Codice_Form(forms.Form):
    number = forms.CharField(label='number')
    codice = forms.CharField(label='codice')

class Chat_id_Form(forms.Form):
    chatid = forms.IntegerField(label='chatid')
