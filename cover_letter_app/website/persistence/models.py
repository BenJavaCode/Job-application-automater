from .. import db
from flask_login import UserMixin
from sqlalchemy.sql import func

"""_summary_:
    Object models for relational database, compatible with MySQL or PostrgeSQL.
"""

class User(db.Model, UserMixin):
    # Unique
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    # Non unique
    password = db.Column(db.String(254), nullable=False)
    education = db.Column(db.String(254), nullable=False, default='')
    real_name = db.Column(db.String(254), nullable=False, default='')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    #RELATIONS
    competencesets = db.relationship('Competenceset', backref='user', lazy=True, passive_deletes=True)
    scrapingqueries = db.relationship('Scrapingquery', backref='user', lazy=True, passive_deletes=True)
        
    def __repr__(self):
        return 'Username: {} email: {} creationdate: {} education: {} real_name {}'.format(
            self.username, self.email, self.date_created, self.education, self.real_name
        )
    
    
class Competenceset(db.Model):
    # Unique
    id = db.Column(db.Integer, primary_key=True)
    # Non unique 
    name = db.Column(db.String(150), nullable=False)
    set_type = db.Column(db.Integer, nullable=False)
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    #RELATIONS
    competence = db.relationship('Competence', backref='competenceset', lazy=True, passive_deletes=True)

       
class Competence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Non unique
    text = db.Column(db.String(300), nullable=False)
    # Foreign keys
    competenceset_id = db.Column(db.Integer, db.ForeignKey('competenceset.id', ondelete='CASCADE'), nullable=False)
    
# Association table for scrapingquery - geography realtion       
geographies = db.Table('geographies',
    db.Column('scrapingquery_id', db.Integer, db.ForeignKey('scrapingquery.id'), primary_key=True),
    db.Column('geography_id', db.Integer, db.ForeignKey('geography.id'), primary_key=True)
)


class Scrapingquery(db.Model): 
    # Unique
    id = db.Column(db.Integer, primary_key=True)
    # Non unique
    name = db.Column(db.String(150),  nullable=False)
    age = db.Column(db.Integer, nullable=False) 
    category = db.Column(db.String(150), nullable=False) 
    criterias = db.Column(db.String(4096), nullable=False) # Is not its own table, because of how it is used.
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    # RELATIONSHIPS, one-to-many
    jobposts = db.relationship('Jobpost', backref='scrapingquery', lazy=True, passive_deletes=True)
    # many-to-many
    geographies = db.relationship('Geography', secondary=geographies, lazy=True, backref=db.backref('scrapingqueries', lazy=True))
    
    def to_dict(self):
        return {'id':id,'category':self.category,'age':self.age,
                    'criterias':self.criterias, 'geographies':[geo.name for geo in self.geographies]}
    

class Geography(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)


class Jobpost(db.Model):
    # Unique
    id = db.Column(db.Integer, primary_key=True)
    # Non unique
    unique_identifier = db.Column(db.String(4096), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    # Foreign keys
    scrapingquery_id = db.Column(db.Integer, db.ForeignKey('scrapingquery.id', ondelete='CASCADE'), nullable=False)


    def to_dict(self):
        return {'id':self.id,'unique_identifier':self.unique_identifier,
                    'url':self.url, 'status':self.status, 'scrapingquery_id':self.scrapingquery_id}

    
    
    
    
    
    
    
    

    
    