from django.db import models

class Session(models.Model):
    session_id=models.AutoField(primary_key=True, default=None)
    phone_number=models.CharField(max_length=14, default=None)
class Contact(models.Model):
    contact_id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=30)
    num=models.CharField(max_length=14, default="", null=True)
    path=models.CharField(default="", max_length=1000)
    session_id=models.ForeignKey(Session, on_delete=models.CASCADE)
    num_bottone=models.IntegerField(default=0)
class Message(models.Model):
    message_id=models.IntegerField(primary_key=True)
    testo=models.CharField(max_length=8000)
    date=models.DateTimeField(auto_now=False)
    cont_id=models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='from_id', default=None)
    out=models.BooleanField()
    path=models.CharField(max_length=800, default=None)
