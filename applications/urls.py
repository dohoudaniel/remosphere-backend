from rest_framework import routers
from .views import ApplicationViewSet

router = routers.DefaultRouter()
router.register(r"applications", ApplicationViewSet, basename="applications")

urlpatterns = router.urls
