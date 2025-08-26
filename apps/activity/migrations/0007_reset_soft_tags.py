from django.db import migrations

NEW_SOFT = [
    "문제 해결",
    "의사소통",
    "팀워크/협업",
    "자기관리",
    "작업습관",
    "비즈니스",
]

def forwards(apps, schema_editor):
    Tag = apps.get_model("activity", "Tag")
    # 기존 soft 전부 삭제
    Tag.objects.filter(kind="soft").delete()
    # 우리가 정한 6개만 재생성
    for name in NEW_SOFT:
        Tag.objects.update_or_create(name=name, defaults={"kind": "soft"})

def backwards(apps, schema_editor):
    # 롤백 시 별도 복원 없음(필요하면 여기에 OLD_SOFT 복원코드 넣어도 됨)
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("activity", "0006_update_soft_tags"),  # 직전 번호에 맞추세요
    ]
    operations = [
        migrations.RunPython(forwards, backwards),
    ]
