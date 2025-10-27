from django.urls import path
from .views import (
    PortfolioListCreateAPIView,
    PortfolioDetailAPIView,
    PortfolioAddActivityAPIView,
    PortfolioRemoveActivityAPIView,
    # ERD 확장: 프로젝트
    ProjectCategoryListAPIView,
    ProjectListCreateAPIView,
    ProjectDetailAPIView,
    ProjectAddActivityAPIView,
    ProjectRemoveActivityAPIView,
)

urlpatterns = [
    path('',              PortfolioListCreateAPIView.as_view(),    name='portfolio-list'),
    path('<int:pk>/',     PortfolioDetailAPIView.as_view(),        name='portfolio-detail'),
    path('<int:pk>/add-activity/',    PortfolioAddActivityAPIView.as_view(),    name='portfolio-add-activity'),
    path('<int:pk>/remove-activity/', PortfolioRemoveActivityAPIView.as_view(), name='portfolio-remove-activity'),
    # 프로젝트
    path('projects/categories/',   ProjectCategoryListAPIView.as_view(), name='project-category-list'),
    path('projects/',              ProjectListCreateAPIView.as_view(),  name='project-list-create'),
    path('projects/<int:pk>/',     ProjectDetailAPIView.as_view(),      name='project-detail'),
    path('projects/<int:pk>/add-activity/',    ProjectAddActivityAPIView.as_view(),    name='project-add-activity'),
    path('projects/<int:pk>/remove-activity/', ProjectRemoveActivityAPIView.as_view(), name='project-remove-activity'),
]
