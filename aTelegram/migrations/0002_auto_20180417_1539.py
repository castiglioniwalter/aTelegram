# Generated by Django 2.0.3 on 2018-04-17 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aTelegram', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_id',
            field=models.AutoField(default=None, primary_key=True, serialize=False),
        ),
    ]