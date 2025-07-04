# import os
# import sys


# sys.path.insert(0, os.path.dirname(__file__))


# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     message = 'It works!\n'
#     version = 'Python %s\n' % sys.version.split()[0]
#     response = '\n'.join([message, version])
#     return [response.encode()]




# import sys
# import os

# # Add your project directory to the Python path
# project_path = '/home/ainstack/core/djangoML'
# if project_path not in sys.path:
#     sys.path.insert(0, project_path)

# # Set environment variable to tell Django where settings module is
# os.environ['DJANGO_SETTINGS_MODULE'] = 'djangoML.settings'

# # Activate your virtual environment
# activate_this = '/home/ainstack/virtualenv/core/djangoML/3.9/bin/activate_this.py'
# with open(activate_this) as file_:
#     exec(file_.read(), dict(__file__=activate_this))

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()




import sys
import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Step 1: Activate virtual environment FIRST
activate_this = '/home/ainstack/virtualenv/core/djangoML/3.9/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

# Step 2: Add project path to Python path
sys.path.insert(0, '/home/ainstack/core/djangoML')

# Step 3: Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoML.settings")

# Step 4: Get WSGI application (do NOT call django.setup())
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


