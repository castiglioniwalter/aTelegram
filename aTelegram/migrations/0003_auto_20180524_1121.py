# Generated by Django 2.0.3 on 2018-05-24 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aTelegram', '0002_auto_20180417_1539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='contact_id',
        ),
        migrations.AddField(
            model_name='contact',
            name='num_bottone',
            field=models.IntegerField(default=None),
        ),
    ]
