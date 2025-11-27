from rest_framework import routers
from .views import CompanyViewSet

router = routers.DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")

urlpatterns = router.urls
