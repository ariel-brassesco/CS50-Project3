from .models import Place
from django.conf import settings

def place_info(request):
    return {
        'PLACE': Place.objects.select_related().first(),
        }


