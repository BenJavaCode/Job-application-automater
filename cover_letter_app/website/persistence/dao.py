from .models import Competenceset, Geography, Jobpost, Scrapingquery, User, Competence
from .. import db
from flask_login import current_user



class ModelDao():
    
    def __init__(self, model):
        self.model = model
    
    def get_by_id(self, id) -> db.Model:
        return self.model.query.get(id)
        
    def get_first_where(self, **kwargs) -> db.Model:
        return self.model.query.filter_by(**kwargs).first()
    
    def get_all_where(self, **kwargs) -> list:
        return self.model.query.filter_by(**kwargs).all()
    
    def create_new(self, **kwargs) -> db.Model:
        new_model = self.model(**kwargs)
        return new_model

    def save(self, model) -> None:
        db.session.add(model)
        db.session.commit()
        
    def save_all(self, models) -> None:
        db.session.add_all(models)
        db.session.commit()
        
    
    def delete(self, model_instance) -> None:
        db.session.delete(model_instance)
        db.session.commit()
    
    def delete_by_id(self, id) -> None:
        db.session.delete(self.model.query.get(id))
        db.session.commit()
            
    def delete_first_where(self, **kwargs) -> None:
        db.session.delete(self.model.query.filter_by(**kwargs).first())
        db.session.commit()
    
    def delete_all_where(self, **kwargs) -> None:
        db.session.delete(self.model.query.filter_by(**kwargs).all())
        db.session.commit()
        
    def delete_all(self, models) -> None:
        for model in models :
            db.session.delete(model)
        db.session.commit()
    
    def update_where(self, id, **kwargs) -> None:
        instance = self.model.query.get(id)
        for k,v in kwargs.items():
            setattr(instance, k, v)
        db.session.commit()
        
        
class UserDao(ModelDao):
    
    def current_user_repr(self) -> dict:
        user = current_user 
        return {key:val for (key,val) in user.__dict__.items() if key != '_sa_instance_state'}
    
    def update_current_user(self, **kwargs) -> None:
        user = current_user
        for k,v in kwargs.items():
            setattr(user, k, v)
        db.session.commit()
        
    def get_user_attr(self, attr: str): 
        return getattr(current_user, attr)
    
    def get_user(self) -> User:
        return current_user
    
    

    
user_dao = UserDao(User)

jobpost_dao = ModelDao(Jobpost)
scrapingquery_dao = ModelDao(Scrapingquery)
competenceset_dao = ModelDao(Competenceset)
competence_dao = ModelDao(Competence)
geography_dao = ModelDao(Geography)


    

        
    