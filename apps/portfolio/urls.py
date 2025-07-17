from django.urls import path
from .views import (
    PortfolioListCreateAPIView,
    PortfolioDetailAPIView,
    PortfolioAddActivityAPIView,
    PortfolioRemoveActivityAPIView,
)

urlpatterns = [
    path('',              PortfolioListCreateAPIView.as_view(),    name='portfolio-list'),
    path('<int:pk>/',     PortfolioDetailAPIView.as_view(),        name='portfolio-detail'),
    path('<int:pk>/add-activity/',    PortfolioAddActivityAPIView.as_view(),    name='portfolio-add-activity'),
    path('<int:pk>/remove-activity/', PortfolioRemoveActivityAPIView.as_view(), name='portfolio-remove-activity'),
]
