from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("activity", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="활동명")),
                ("summary", models.CharField(blank=True, max_length=255, verbose_name="요약")),
                ("period_start", models.DateField(blank=True, null=True, verbose_name="시작일")),
                ("period_end", models.DateField(blank=True, null=True, verbose_name="종료일")),
                ("is_ongoing", models.BooleanField(default=False, verbose_name="진행 중 여부")),
                ("metric", models.CharField(blank=True, max_length=255, verbose_name="성과 지표")),
                ("hard_tools", models.CharField(blank=True, max_length=255, verbose_name="핸즈온 스택")),
                ("soft_skills", models.CharField(blank=True, max_length=255, verbose_name="소프트 스킬")),
                ("situation", models.TextField(blank=True, verbose_name="상황")),
                ("task_detail", models.TextField(blank=True, verbose_name="과제")),
                ("action_detail", models.TextField(blank=True, verbose_name="행동")),
                ("result_detail", models.TextField(blank=True, verbose_name="결과")),
                ("takeaway", models.TextField(blank=True, verbose_name="교훈")),
                (
                    "attachment",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="subactivity_attachments/",
                        verbose_name="첨부 파일",
                    ),
                ),
                ("link_url", models.URLField(blank=True, verbose_name="관련 링크")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sub_activities",
                        to="activity.activity",
                    ),
                ),
            ],
            options={
                "ordering": ["period_start", "id"],
            },
        ),
    ]

