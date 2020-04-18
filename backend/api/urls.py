from rest_framework import routers

from api.viewsets import EmailViewSet

router = routers.SimpleRouter()
router.register('emails', EmailViewSet)

urlpatterns = router.urls
