from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import Email
from api.serializers import EmailSerializer, SMTPSerializer, AttachmentSerializer


class EmailViewSet(mixins.UpdateModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet
                   ):
    queryset = Email.objects.order_by('pk')
    serializer_class = EmailSerializer

    @swagger_auto_schema(responses={200: EmailSerializer(many=True)})
    @action(methods=['POST'], detail=False, serializer_class=SMTPSerializer)
    def send(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={204: None})
    @action(methods=['PUT'],
            detail=True,
            parser_classes=[MultiPartParser, FormParser],
            serializer_class=AttachmentSerializer
            )
    def add_attachment(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
