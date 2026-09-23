import os
from waitress import serve
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # ajuste o nome do módulo de settings
application = get_wsgi_application()

if __name__ == '__main__':
    serve(application, host='127.0.0.1', port=8002, threads=8)