# Generated by Django 4.2.13 on 2024-11-03 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apistatus',
            name='last_checked',
        ),
        migrations.AddField(
            model_name='apilog',
            name='client_id',
            field=models.CharField(blank=True, help_text='Client ID of the device', max_length=100),
        ),
        migrations.AddField(
            model_name='apilog',
            name='keepalive',
            field=models.IntegerField(blank=True, help_text='Keepalive interval of the client in seconds', null=True),
        ),
        migrations.AddField(
            model_name='apilog',
            name='peername',
            field=models.CharField(blank=True, help_text='Socket information of the client', max_length=100),
        ),
        migrations.AddField(
            model_name='apilog',
            name='proto_ver',
            field=models.IntegerField(blank=True, help_text='MQTT protocol version used by the client', null=True),
        ),
        migrations.AddField(
            model_name='apilog',
            name='reason',
            field=models.CharField(blank=True, help_text='Reason for disconnection, if applicable', max_length=100),
        ),
        migrations.AddField(
            model_name='apilog',
            name='sockname',
            field=models.CharField(blank=True, help_text='Socket information of the broker', max_length=100),
        ),
        migrations.AddField(
            model_name='apilog',
            name='username',
            field=models.CharField(blank=True, help_text='Username used by the client', max_length=100),
        ),
        migrations.AddField(
            model_name='apistatus',
            name='client_id',
            field=models.CharField(blank=True, help_text='Client ID of the device', max_length=100),
        ),
        migrations.AddField(
            model_name='apistatus',
            name='keepalive',
            field=models.IntegerField(blank=True, help_text='Keepalive interval of the client in seconds', null=True),
        ),
        migrations.AddField(
            model_name='apistatus',
            name='proto_ver',
            field=models.IntegerField(blank=True, help_text='MQTT protocol version used by the client', null=True),
        ),
        migrations.AddField(
            model_name='apistatus',
            name='username',
            field=models.CharField(blank=True, help_text='Username used by the client', max_length=100),
        ),
        migrations.AlterField(
            model_name='apilog',
            name='event',
            field=models.CharField(choices=[('client.connected', 'Connected'), ('client.disconnected', 'Disconnected'), ('client.connack', 'Connack')], help_text='Event type', max_length=50),
        ),
    ]
