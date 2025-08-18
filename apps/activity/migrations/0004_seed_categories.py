from django.db import migrations

CATEGORIES = [
    ("study", "학업"),
    ("campus", "교내 활동"),
    ("external", "대외 활동"),
    ("school_project", "학교 프로젝트"),
    ("education", "교육"),
    ("club", "동아리"),
    ("contest", "공모전/대회"),
    ("award", "수상"),
    ("certificate", "자격증"),
    ("parttime", "아르바이트"),
    ("intern", "인턴"),
    ("contract", "계약직/파견직"),
    ("fulltime", "정규직"),
    ("side_project", "사이드 프로젝트"),
    ("rnd", "연구개발"),
    ("startup", "사업/창업"),
    ("etc", "기타"),
]

def seed(apps, schema_editor):
    Category = apps.get_model("activity", "ActivityCategory")
    for idx, (key, name) in enumerate(CATEGORIES, start=1):
        Category.objects.get_or_create(key=key, defaults={"name": name, "order": idx})

def unseed(apps, schema_editor):
    Category = apps.get_model("activity", "ActivityCategory")
    Category.objects.filter(key__in=[k for k, _ in CATEGORIES]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("activity", "0003_activitycategory_tag_activity_category_activity_tags"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
