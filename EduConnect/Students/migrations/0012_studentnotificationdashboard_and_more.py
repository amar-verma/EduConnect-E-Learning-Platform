# Generated by Django 5.1.3 on 2025-03-06 07:19

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0011_alter_payment_amount'),
        ('Teachers', '0002_alter_receivedpayment_duration'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentNotificationDashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify_by_teacher', to='Students.student')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherNotificationDashBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=False)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify_by_student', to='Teachers.teacher')),
            ],
        ),
    ]
