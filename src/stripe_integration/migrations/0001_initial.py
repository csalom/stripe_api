# Generated by Django 3.2.6 on 2021-08-21 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last update')),
                ('stripe_id', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('invoice_prefix', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last update')),
                ('stripe_id', models.CharField(max_length=100)),
                ('last_digits', models.CharField(help_text='Only save 4 last characters because of security reasons', max_length=4)),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last update')),
                ('stripe_id', models.CharField(max_length=100)),
                ('price_id', models.CharField(max_length=100, verbose_name='Stripe Price ID')),
                ('status', models.CharField(choices=[('incomplete', 'Incomplete'), ('incomplete_expired', 'Incomplete expired'), ('trialing', 'Trialing'), ('active', 'Active'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('unpaid', 'Unpaid')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stripe_integration.customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stripe_integration.paymentmethod'),
        ),
    ]
