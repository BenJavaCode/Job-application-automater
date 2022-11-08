DB_NAME = 'cl'
GEOGRAPHIES = ['Storkøbenhavn', 'Nordsjælland', 'Sjælland', 'Fyn',
               'Nordjylland','Midtjylland','Sydjylland', 'Bornholm',
               'Skåne', 'Grønland','Færøerne','Udlandet','Danmark']

OPENAI_API_KEY = "your-oenai-key"



class Config:
    """Base config, uses staging database server."""
    TESTING = False
    DB_SERVER = 'localhost'
    DB_NAME = DB_NAME
    SECRET_KEY = 'bitch'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    username = 'root'
    password = 'your-password'

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # Note: all caps
        return f'mysql+pymysql://{self.username}:{self.password}@{self.DB_SERVER}/{DB_NAME}'

class ProductionConfig(Config):
    """Uses production database server."""
    DB_SERVER = '192.168.19.32'

class DevelopmentConfig(Config):
    DB_SERVER = 'localhost'

class TestingConfig(Config):
    DB_SERVER = 'localhost'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
