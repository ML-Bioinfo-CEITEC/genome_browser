from sqlalchemy.engine import url
from db.secrets import SECRET_KEY, POSTGRES

SQLALCHEMY_DATABASE_URL = url.URL(
        drivername="postgres",
        username=POSTGRES['user'], 
        password=POSTGRES['pw'],  
        host=POSTGRES['host'],  
        port=POSTGRES['port'], 
        database=POSTGRES['db'] 
    )
    
SQLALCHEMY_DATABASE_URL_PUBLIC = url.URL(
        drivername="postgres",
        username=POSTGRES['user'], 
        password=POSTGRES['pw'],  
        host=POSTGRES['public host'],  
        port=POSTGRES['port'], 
        database=POSTGRES['db'] 
    )


