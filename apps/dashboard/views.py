from datetime import datetime

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.activity.models import Activity, Award, Certification, GlobalExp, ForeignLang
from apps.portfolio.models import Portfolio, Project
from apps.user.models import Skill
from apps.dashboard.models import ExperienceNote, GoalVision
from apps.dashboard.serializers import ExperienceNoteSerializer, ActivityBoardSerializer, GoalVisionSerializer


class HomeSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        payload = {
            "projects": Project.objects.filter(user=user).count(),
            "portfolios": Portfolio.objects.filter(user=user).count(),
            "experiences": Activity.objects.filter(user=user, is_deleted=False).count(),
            "awards": Award.objects.filter(user=user).count(),
            "certifications": Certification.objects.filter(user=user).count(),
            "languages": ForeignLang.objects.filter(user=user).count(),
            "global_experiences": GlobalExp.objects.filter(user=user).count(),
            "skills": Skill.objects.filter(users=user).count(),
        }
        return Response({"counts": payload})


class ExperienceNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_target_date(self, request, default=None):
        param = request.query_params.get("date") or request.data.get("date")
        if param:
            try:
                return datetime.fromisoformat(param).date()
            except ValueError:
                pass
        return default or timezone.localdate()

    def get(self, request):
        target_date = self._get_target_date(request)
        note = ExperienceNote.objects.filter(user=request.user, date=target_date).first()
        data = ExperienceNoteSerializer(note).data if note else None
        return Response({"date": target_date.isoformat(), "note": data})

    def put(self, request):
        user = request.user
        target_date = self._get_target_date(request)
        payload = request.data.copy()
        payload["date"] = target_date.isoformat()
        note, _ = ExperienceNote.objects.get_or_create(user=user, date=target_date)
        serializer = ExperienceNoteSerializer(
            instance=note,
            data=payload,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data)


class ExperienceBoardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = Activity.objects.filter(user=user)
        ordering = ["board_order", "-updated_at"]
        data = {
            "in_progress": ActivityBoardSerializer(
                qs.filter(status=Activity.Status.IN_PROGRESS, is_deleted=False).order_by(*ordering), many=True
            ).data,
            "highlight": ActivityBoardSerializer(
                qs.filter(status=Activity.Status.HIGHLIGHT, is_deleted=False).order_by(*ordering), many=True
            ).data,
            "completed": ActivityBoardSerializer(
                qs.filter(status=Activity.Status.COMPLETED, is_deleted=False).order_by(*ordering), many=True
            ).data,
            "deleted": ActivityBoardSerializer(
                qs.filter(is_deleted=True).order_by(*ordering), many=True
            ).data,
        }
        return Response(data)

    def patch(self, request):
        user = request.user
        items = request.data if isinstance(request.data, list) else request.data.get("items", [])
        updated_instances = []
        for item in items:
            activity_id = item.get("id")
            if not activity_id:
                continue
            try:
                activity = Activity.objects.get(pk=activity_id, user=user)
            except Activity.DoesNotExist:
                continue
            fields = {}
            if "status" in item:
                if item["status"] not in Activity.Status.values:
                    continue
                fields["status"] = item["status"]
            if "board_order" in item:
                try:
                    fields["board_order"] = int(item["board_order"])
                except (TypeError, ValueError):
                    pass
            if "is_deleted" in item:
                fields["is_deleted"] = bool(item["is_deleted"])
            if not fields:
                continue
            for key, value in fields.items():
                setattr(activity, key, value)
            activity.save(update_fields=list(fields.keys()))
            updated_instances.append(activity)
        serializer = ActivityBoardSerializer(updated_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GoalVisionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goal, _ = GoalVision.objects.get_or_create(user=request.user)
        return Response(GoalVisionSerializer(goal).data)

    def put(self, request):
        goal, _ = GoalVision.objects.get_or_create(user=request.user)
        serializer = GoalVisionSerializer(goal, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    def patch(self, request):
        goal, _ = GoalVision.objects.get_or_create(user=request.user)
        serializer = GoalVisionSerializer(goal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)
