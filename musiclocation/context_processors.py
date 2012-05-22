from django.conf import settings

def deezer_variables(request):
    result = {'DEEZER_APP_ID':settings.DEEZER_APP_ID, 'DEEZER_CHANNEL_URL':settings.DEEZER_CHANNEL_URL}
    return result