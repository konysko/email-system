from rest_framework import viewsets, status
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from api.models import Email
from api.serializers import EmailSerializer, SMTPSerializer


class EmailViewSet(mixins.UpdateModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet
                   ):
    queryset = Email.objects.order_by('pk')
    serializer_class = EmailSerializer

    @action(methods=['POST'], detail=False, serializer_class=SMTPSerializer)
    def send(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)

    @action(methods=['PUT'], detail=True, parser_classes=[FileUploadParser])
    def add_attachment(self, request, *args, **kwargs):
        instance = self.get_object()
        attachment = request.data['file']
        instance.attachment = attachment
        instance.save()
        return Response()
