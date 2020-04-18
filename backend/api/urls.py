from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers

from api.viewsets import EmailViewSet

schema_view = get_schema_view(openapi.Info(
    title="Emails API",
    default_version='v1',
))

router = routers.SimpleRouter()
router.register('emails', EmailViewSet)

urlpatterns = [
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
] + router.urls
