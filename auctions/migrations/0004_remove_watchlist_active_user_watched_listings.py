# Generated by Django 4.1.4 on 2022-12-22 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_listing_created_at_watchlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='active',
        ),
        migrations.AddField(
            model_name='user',
            name='watched_listings',
            field=models.ManyToManyField(blank=True, related_name='watched_by', to='auctions.listing'),
        ),
    ]
