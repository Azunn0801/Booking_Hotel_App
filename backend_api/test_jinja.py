import sys
sys.path.append('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/backend_api')
from app.main import templates
import traceback

try:
    templates.env.get_template('index.html').render({'request': None, 'user': None})
    print('SUCCESS')
except Exception as e:
    traceback.print_exc()
