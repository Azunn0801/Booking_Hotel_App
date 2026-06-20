import sys
sys.path.append('d:/4Study/PTIT/Year 2/Semester 2/Phat trien huong dich vu/Hotel App/backend_api')
from app.database import SessionLocal
from app import models
from sqlalchemy import or_

db = SessionLocal()
keywords = ['vung tau', 'vũng tàu']
query = db.query(models.Property).filter(models.Property.status == 'Approved')
conditions = [models.Property.city.ilike(f'%{kw}%') for kw in keywords] + [models.Property.address.ilike(f'%{kw}%') for kw in keywords]
query = query.filter(or_(*conditions))

try:
    res = query.all()
    print('Success:', len(res))
except Exception as e:
    print('Error:', repr(e))
