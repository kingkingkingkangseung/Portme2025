from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activity", "0010_update_categories_for_new_design"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="subject",
            field=models.CharField(blank=True, max_length=200, verbose_name="주제"),
        ),
        migrations.AddField(
            model_name="activity",
            name="host",
            field=models.CharField(blank=True, max_length=200, verbose_name="주최/주관"),
        ),
        migrations.AddField(
            model_name="activity",
            name="work_title",
            field=models.CharField(blank=True, max_length=200, verbose_name="출품작/프로젝트명"),
        ),
        migrations.AddField(
            model_name="activity",
            name="participation_type",
            field=models.CharField(
                blank=True,
                choices=[("team", "팀"), ("individual", "개인")],
                max_length=20,
                verbose_name="참여 형태",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="is_awarded",
            field=models.BooleanField(default=False, verbose_name="수상 여부"),
        ),
        migrations.AddField(
            model_name="activity",
            name="award_detail",
            field=models.CharField(blank=True, max_length=200, verbose_name="수상 내역"),
        ),
        migrations.AddField(
            model_name="activity",
            name="situation",
            field=models.TextField(blank=True, verbose_name="상황(Situation)"),
        ),
        migrations.AddField(
            model_name="activity",
            name="task_detail",
            field=models.TextField(blank=True, verbose_name="과제(Task)"),
        ),
        migrations.AddField(
            model_name="activity",
            name="action_detail",
            field=models.TextField(blank=True, verbose_name="행동(Action)"),
        ),
        migrations.AddField(
            model_name="activity",
            name="result_detail",
            field=models.TextField(blank=True, verbose_name="결과(Result)"),
        ),
    ]
