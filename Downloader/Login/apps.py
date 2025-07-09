from django.apps import AppConfig
from django.conf import settings


class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Login'

    def ready(self):
        import netifaces
        settings.ALLOWED_HOSTS=[]
        settings.CSRF_TRUSTED_ORIGINS = []
        for interface in netifaces.interfaces():
            interface_info = netifaces.ifaddresses(interface)
            if interface_info.get (netifaces.AF_INET) != None:
                ip = interface_info.get(netifaces.AF_INET)[0]['addr']
                settings.ALLOWED_HOSTS.append(ip)
                settings.CSRF_TRUSTED_ORIGINS.append('https://'+ip)