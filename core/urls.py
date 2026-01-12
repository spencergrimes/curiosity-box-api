from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChildViewSet,
    LoginView,
    LogoutView,
    QuestionViewSet,
    RegisterView,
    TopicCategoryViewSet,
)
from .views.health import health_check, liveness_check, readiness_check

router = DefaultRouter()
router.register(r"children", ChildViewSet)
router.register(r"topics", TopicCategoryViewSet)
router.register(r"questions", QuestionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Authentication endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # Health check endpoints (for K8s/Docker/load balancers)
    path("health/", health_check, name="health-check"),
    path("health/ready/", readiness_check, name="readiness-check"),
    path("health/live/", liveness_check, name="liveness-check"),
]
