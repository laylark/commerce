# Generated by Django 4.1.4 on 2022-12-29 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_user_watched_listings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='watched_listings',
            field=models.ManyToManyField(blank=True, related_name='watched_by', to='auctions.listing'),
        ),
    ]
