from django.db import migrations

# 새로 유지할 소프트 태그(최종 집합)
NEW_SOFT = [
    "문제 해결",
    "의사소통",
    "팀워크/협업",
    "자기관리",
    "작업습관",
    "비즈니스",
]

# (선택) 롤백 시 복원할 예전 소프트 태그
OLD_SOFT = [
    "자기개발/성장", "커뮤니케이션", "문제 해결 능력", "리더십", "팀워크",
    "주도성/오너십", "기획", "발표", "협업", "시간관리", "책임감",
    "갈등관리", "적응력", "고객집중", "데이터 기반 사고", "디테일/정확성",
]

def forwards(apps, schema_editor):
    Tag = apps.get_model("activity", "Tag")
    for name in NEW_SOFT:
        Tag.objects.update_or_create(name=name, defaults={"kind": "soft"})
    Tag.objects.filter(kind="soft").exclude(name__in=NEW_SOFT).delete()

def backwards(apps, schema_editor):
    Tag = apps.get_model("activity", "Tag")
    for name in OLD_SOFT:
        Tag.objects.get_or_create(name=name, defaults={"kind": "soft"})
    Tag.objects.filter(kind="soft", name__in=NEW_SOFT).exclude(name__in=OLD_SOFT).delete()

class Migration(migrations.Migration):

    dependencies = [
        # 여기를 "현재 activity의 직전 마이그"로 맞추세요. 예: ('activity', '0005_seed_tags')
        ('activity', '0005_seed_tags'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
