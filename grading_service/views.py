from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    return JsonResponse(
        {
            "status": "UP",
            "service": "grading_service",
            "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        status=200,
    )
