from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0004_seed_jobroles"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="display_name",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="github_linked",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="level",
        ),
        migrations.RemoveField(
            model_name="profile",
            name="website",
        ),
        migrations.AddField(
            model_name="profile",
            name="admission_date",
            field=models.DateField(blank=True, null=True, verbose_name="입학 연월"),
        ),
        migrations.AddField(
            model_name="profile",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="생년월일"),
        ),
        migrations.AddField(
            model_name="profile",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="연락 이메일"),
        ),
        migrations.AddField(
            model_name="profile",
            name="graduation_date",
            field=models.DateField(blank=True, null=True, verbose_name="졸업 연월"),
        ),
        migrations.AddField(
            model_name="profile",
            name="phone_number",
            field=models.CharField(blank=True, max_length=20, verbose_name="전화번호"),
        ),
        migrations.AddField(
            model_name="profile",
            name="school_name",
            field=models.CharField(blank=True, max_length=120, verbose_name="학교명"),
        ),
        migrations.CreateModel(
            name="ProfileLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(blank=True, max_length=50, verbose_name="링크 이름")),
                ("url", models.URLField(verbose_name="URL")),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "profile",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="links", to="profiles.profile"),
                ),
            ],
            options={
                "ordering": ["order", "id"],
            },
        ),
    ]
