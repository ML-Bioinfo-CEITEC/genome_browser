import db.models

db.models.Base.metadata.create_all(bind=db.models.engine)