from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("activity", "0006_award_issuer_award_link_url_certification_link_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="activity_type",
            field=models.CharField(
                choices=[
                    ("PROJECT", "프로젝트"),
                    ("CONTEST", "공모전"),
                    ("EXTRACURRICULAR", "대외활동"),
                    ("CAMPUS", "교내활동"),
                    ("CLUB", "동아리"),
                    ("HACKATHON", "해커톤"),
                    ("RESEARCH", "연구"),
                    ("EDUCATION", "교육"),
                    ("STARTUP", "창업"),
                    ("VOLUNTEER", "봉사"),
                    ("OTHER", "기타"),
                ],
                default="PROJECT",
                max_length=20,
                verbose_name="활동 타입",
            ),
        ),
    ]
