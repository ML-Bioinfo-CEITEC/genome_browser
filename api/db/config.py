from sqlalchemy.engine import url
from db.secrets import SECRET_KEY, POSTGRES

deploy_mode = True

SQLALCHEMY_DATABASE_URL_APPENGINE = url.URL(
        drivername="postgres",
        username=POSTGRES['user'], 
        password=POSTGRES['pw'],  
        host=POSTGRES['host'],  
        port=POSTGRES['port'], 
        database=POSTGRES['db'] 
    )
    
SQLALCHEMY_DATABASE_URL_LOCAL = url.URL(
        drivername="postgres",
        username=POSTGRES['user'], 
        password=POSTGRES['pw'],  
        host=POSTGRES['public host'],  
        port=POSTGRES['port'], 
        database=POSTGRES['db'] 
    )


if deploy_mode:
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL_APPENGINE
else:
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL_LOCAL
    

