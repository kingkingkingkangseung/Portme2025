from django.db import migrations

# 원하는 만큼 수정해도 됩니다 (이름은 유니크)
TAGS = [
    # ---- Soft (행동/역량) ----
    ("자기개발/성장", "soft"),
    ("커뮤니케이션", "soft"),
    ("문제 해결 능력", "soft"),
    ("리더십", "soft"),
    ("팀워크", "soft"),
    ("주도성/오너십", "soft"),
    ("기획", "soft"),
    ("발표", "soft"),
    ("협업", "soft"),
    ("시간관리", "soft"),
    ("책임감", "soft"),
    ("갈등관리", "soft"),
    ("적응력", "soft"),
    ("고객집중", "soft"),
    ("데이터 기반 사고", "soft"),
    ("디테일/정확성", "soft"),

    # ---- Hard (기술/도구) ----
    ("Python", "hard"),
    ("Django", "hard"),
    ("DRF", "hard"),
    ("FastAPI", "hard"),
    ("JavaScript", "hard"),
    ("TypeScript", "hard"),
    ("React", "hard"),
    ("Next.js", "hard"),
    ("Node.js", "hard"),
    ("Express", "hard"),
    ("HTML/CSS", "hard"),
    ("Tailwind CSS", "hard"),
    ("SQL", "hard"),
    ("MySQL", "hard"),
    ("PostgreSQL", "hard"),
    ("SQLite", "hard"),
    ("MongoDB", "hard"),
    ("Redis", "hard"),
    ("Docker", "hard"),
    ("Kubernetes", "hard"),
    ("AWS", "hard"),
    ("Git", "hard"),
    ("GitHub Actions", "hard"),
    ("Linux", "hard"),
    ("Nginx", "hard"),
    ("Gunicorn", "hard"),
]

def seed(apps, schema_editor):
    Tag = apps.get_model("activity", "Tag")
    for name, kind in TAGS:
        Tag.objects.get_or_create(name=name, defaults={"kind": kind})

def unseed(apps, schema_editor):
    Tag = apps.get_model("activity", "Tag")
    Tag.objects.filter(name__in=[n for n, _ in TAGS]).delete()

class Migration(migrations.Migration):
    dependencies = [
        # ⬇️ 직전 마이그레이션 파일명으로 바꾸세요 (예: "0004_seed_categories")
        ("activity", "0004_seed_categories"),
    ]
    operations = [migrations.RunPython(seed, unseed)]
