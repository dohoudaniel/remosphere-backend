from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Root of the API. Provides a welcome message and points to docs.
    """
    # return Response({
    #     "message": "Welcome to the RemoSphere API! Check out the documentation here:",
    #     "swagger": "/swagger/",
    #     "redoc": "/redocs/",
    #     "docs": "/docs/"
    # })
    return Response({
        "status": "success",
        "message": "Welcome to the RemoSphere API!",
        "documentation": {
            "swagger": request.build_absolute_uri("/swagger/"),
            "redoc": request.build_absolute_uri("/redoc/"),
            "docs": request.build_absolute_uri("/docs/")
        }
    })
