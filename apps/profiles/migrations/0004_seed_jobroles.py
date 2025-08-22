from django.db import migrations

ROLES = {
    "dev": [
        "백엔드 개발자", "프론트엔드 개발자", "풀스택 개발자",
        "Android 개발자", "iOS 개발자", "모바일 앱 개발자",
        "데이터 엔지니어", "데이터 사이언티스트",
        "머신러닝 엔지니어", "AI/ML 엔지니어",
        "DevOps 엔지니어", "SRE", "QA 엔지니어",
        "보안 엔지니어", "DBA",
    ],
    "design": [
        "UI 디자이너", "UX 디자이너", "그래픽 디자이너",
        "BX/BI 디자이너", "영상 디자이너", "편집 디자이너",
        "일러스트레이터", "콘텐츠 디자이너",
    ],
    "pm": [
        "서비스 기획자", "PO(프로덕트 오너)", "PM(프로덕트 매니저)", "UI/UX 기획자",
    ],
    "biz": [
        "CEO", "COO", "CFO", "CSO",
        "경영전략/사업기획", "마케팅/홍보", "영업", "HR",
        "법무/지식재산", "회계/세무/재무",
    ],
    "etc": ["퍼블리셔"],
}

def seed(apps, schema_editor):
    JobRole = apps.get_model("profiles", "JobRole")
    order = 1
    for group, names in ROLES.items():
        for name in names:
            JobRole.objects.get_or_create(
                name=name,
                defaults={"group": group, "order": order, "is_active": True},
            )
            order += 1

def unseed(apps, schema_editor):
    JobRole = apps.get_model("profiles", "JobRole")
    JobRole.objects.filter(name__in=[n for arr in ROLES.values() for n in arr]).delete()

class Migration(migrations.Migration):
    dependencies = [
        # ← 여기를 정확히 “직전 스키마 마이그레이션 파일 이름”으로 바꿔주세요.
        ("profiles", "0003_jobrole_profile_full_name_profile_github_linked_and_more"),
    ]
    operations = [migrations.RunPython(seed, unseed)]