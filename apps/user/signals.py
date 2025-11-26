import logging
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings
from allauth.socialaccount.signals import social_account_added


logger = logging.getLogger(__name__)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    비밀번호 재설정 토큰이 만들어졌을 때 실행됨
    """
    frontend_path = "/reset-password"
    reset_url = f"{settings.FRONTEND_URL.rstrip('/')}{frontend_path}?token={reset_password_token.key}"

    subject = "[PortMe] 비밀번호 재설정 안내"
    text_body = (
        "안녕하세요.\n\n"
        "아래 링크를 클릭하여 새 비밀번호를 설정해주세요.\n"
        f"{reset_url}\n\n"
        "링크가 열리지 않는다면 위 주소를 복사해 브라우저 주소창에 붙여넣어 주세요.\n"
        "본 메일을 요청하지 않았다면 고객센터로 문의해 주세요."
    )
    html_body = (
        f"<p>안녕하세요.</p>"
        f"<p>아래 버튼을 눌러 새 비밀번호를 설정하세요.</p>"
        f'<p><a href="{reset_url}" '
        f'style="display:inline-block;padding:12px 20px;border-radius:6px;'
        f'background:#1da472;color:#fff;text-decoration:none;">비밀번호 재설정</a></p>'
        f"<p>버튼이 작동하지 않으면 다음 주소를 브라우저에 복사해 붙여넣어 주세요.</p>"
        f'<p style="word-break:break-all;">{reset_url}</p>'
        f"<p>요청을 하지 않았다면 고객센터로 문의하시기 바랍니다.</p>"
    )

    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reset_password_token.user.email],
        )
        message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)
    except Exception:
        logger.exception("비밀번호 재설정 이메일 전송 실패")
        raise

@receiver(social_account_added)
def fill_profile_on_social_signup(request, sociallogin, **kwargs):
    user = sociallogin.user
    data = sociallogin.account.extra_data or {}
    full_name = data.get("name") or f"{data.get('given_name','')} {data.get('family_name','')}".strip()
    
    p = getattr(user, "profile", None)
    if p and not p.full_name:
        p.full_name = full_name or p.full_name
        p.save()
