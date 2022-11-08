from ..persistence.dao import user_dao, competenceset_dao, competence_dao, scrapingquery_dao, geography_dao, jobpost_dao
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user

from .webscraping import webscraper
from .cl_gennerator import create_cover_letter
from googletrans import Translator

     
class ResponseBody:
    """_summary_:
        This class is used for all communication between view and services.
        Its purpose is to standardise communication.
    """
    def __init__(self, success_message=None, error_message=None, requested_obj=None, exception=None):
        self.error_message = error_message
        self.success_message = success_message
        self.requested_obj = requested_obj
        self.exception = exception


def request_handler(func):
    """_summary_:
        Decorator used for all service functions, that are not private (that are used directly by views).
        Its purpose is to handle errors that could occur in services or deeper in the application layers.
    Args:
        func (_type_): The service function that is decorated.
    """
    def handle_outcome(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Should be replaced by a logger.
            print(f'An Exception occuried somwhere in the controll stack. the exception is: {e}')
            return ResponseBody(exception=True)
    return handle_outcome


class UserService():
    
    @request_handler
    def update_password(self, current_password, new_password, confirm_password):
        if self.__check_password_correct(current_password):
            if new_password == confirm_password:
                enc_password = generate_password_hash(new_password)
                user_dao.update_current_user(password=enc_password)
                return ResponseBody(success_message='Password succesfully updated')
            else: return ResponseBody(error_message='Passwords do not match')
        else: return ResponseBody(error_message='Password not correct')
        
    @request_handler
    def update_username(self, username):
        if self.__check_username(username):
            user_dao.update_current_user(username=username)
            return ResponseBody(success_message=f'Username changed to {username}')
        else: return ResponseBody(error_message='Username already taken')
    
    @request_handler   
    def update_email(self, email):
        if self.__check_email(email):
            email = str(email).lower()
            user_dao.update_current_user(email=email)
            return ResponseBody(success_message=f'Email changed to {email}')
        else: return ResponseBody(error_message='Email used in another account')
            
    @request_handler    
    def sign_up_user(self, password, confirm_password, username, email):
        if self.__check_username(username):
            if self.__check_email(email):
                email = str(email).lower()
                if password == confirm_password:
                    enc_password = generate_password_hash(password)
                    new_user = user_dao.create_new(username=username,
                                                    email=email,
                                                    password=enc_password)
                    user_dao.save(new_user)
                    login_user(new_user, remember=True)
                    return ResponseBody(success_message='User succesfully created')
                else: return ResponseBody(error_message='Passwords do not match')
            else: return ResponseBody(error_message='Email already in use')
        else: return ResponseBody(error_message='Username already in use')
        
    @request_handler  
    def login_user(self, password, email):
        user = user_dao.get_first_where(email=email)
        if user:
            if self.__check_password_correct(specified_password=password, user=user):
                login_user(user, remember=True)
                return ResponseBody(success_message='Logged in')
            else: return ResponseBody(error_message='Password incorrect')
        else: return ResponseBody(error_message='User does not exist')  
        
    @request_handler
    def current_user_repr(self, exclude: list):
        if exclude:
            user_repr = user_dao.current_user_repr()
            return ResponseBody(requested_obj={key:val for (key,val) in user_repr.items() if key not in exclude})
        return ResponseBody(requested_obj=user_dao.current_user_repr())
    
    def __check_password_correct(self, specified_password, user=False):
        if user: 
            password = user.password
        else: 
            password = user_dao.get_user_attr('password')
        return check_password_hash(password, specified_password)
    
    def __check_username(self, new_username):
        if user_dao.get_first_where(username=new_username):
            return False
        else: return True
    
    def __check_email(self, new_email):
        if user_dao.get_first_where(email=new_email):
            return False
        else: return True
        
        
    @request_handler 
    def get_real_name(self):
        return user_dao.get_user_attr('real_name')
    
    @request_handler
    def get_education(self):
        return user_dao.get_user_attr('education')
    
    @request_handler
    def change_educational_background(self, education_string):
        user_dao.update_current_user(education=education_string)
        return ResponseBody(success_message=f'Educational background changed to {education_string}')
    
    @request_handler
    def change_real_name(self, real_name_string):
        user_dao.update_current_user(real_name=real_name_string)
        return ResponseBody(success_message=f'Name changed to {real_name_string}')

class CompetenceService():

    # SETS 
    @request_handler
    def get_sets(self):
        user_id = user_dao.get_user_attr('id')
        response = ResponseBody(requested_obj=[(s.id, s.name) for s in competenceset_dao.get_all_where(user_id=user_id)])
        return response

    @request_handler
    def get_sets_by_type(self, set_type, json_format=True):
        user_id = user_dao.get_user_attr('id')
        competencesets = competenceset_dao.get_all_where(user_id=user_id, set_type=set_type)
        if json_format:
            initial_option = [{'id':-1, 'name':'--Select Set--'}]
            response = ResponseBody(requested_obj = initial_option +
                                    [{'id': competenceset.id, 'name': competenceset.name } for competenceset in competencesets])
            return response
        else: 
            initial_option = [(-1, '--Select Set--')]
            response = ResponseBody(requested_obj = initial_option + 
                                    [(competenceset.id, competenceset.name ) for competenceset in competencesets])
            return response
    
    @request_handler
    def create_set(self, name, set_type):  
        user_id = user_dao.get_user_attr('id')
        competence_set = competenceset_dao.create_new(user_id=user_id, name=name, set_type=set_type)
        competenceset_dao.save(competence_set)
        return ResponseBody(requested_obj={'id': competence_set.id, 'name': competence_set.name})

    @request_handler
    def delete_competence_set(self, id):
        user_id = user_dao.get_user_attr('id')
        if competenceset_dao.get_first_where(user_id=user_id, id=id):
            competenceset_dao.delete_by_id(id)
            return ResponseBody(success_message='Successfully deleted')
        else: 
            return ResponseBody(error_message='Not Allowed, bad user!')

    # /SETS
    
    # Competences
    @request_handler
    def create_competence(self, text, competenceset_id):
        if competenceset_dao.get_first_where(id=competenceset_id):
            competence = competence_dao.create_new(text=text, competenceset_id=competenceset_id)
            competence_dao.save(competence)
            return ResponseBody(requested_obj={'id':competence.id, 'text': competence.text})
        else: 
            return ResponseBody(error_message='You need to choose first')


    @request_handler
    def delete_competence(self, id, competenceset_id):
        user_id = user_dao.get_user_attr('id')
        if competenceset_dao.get_first_where(user_id=user_id, id=competenceset_id):
            if competence_dao.get_first_where(id=id, competenceset_id=competenceset_id):
                competence_dao.delete_by_id(id)
                return ResponseBody(requested_obj=id)
        return ResponseBody(error_message='Not Allowed, bad user!')
    
    
    @request_handler 
    def get_competences_by_set_id(self, competenceset_id): 
        competences = competence_dao.get_all_where(competenceset_id=competenceset_id)
        response = ResponseBody( requested_obj = 
                                [{'id': competence.id, 'text': competence.text } for competence in competences])
        return response
    
    
    
class ScrapingQueryService():
    
    @request_handler
    def get_queries(self):
        user_id = user_dao.get_user_attr('id')
        queries = scrapingquery_dao.get_all_where(user_id=user_id)
        initial_option = [(-1, '-- Create new --')]
        return ResponseBody(requested_obj=
                                initial_option + [(query.id, query.name) for query in queries])
    
    @request_handler
    def create_query(self, name, age, category, geographies, criterias):
        
        user_id = user_dao.get_user_attr('id')
        query = scrapingquery_dao.create_new(user_id=user_id, name=name, age=age, category=category, criterias=criterias)
            
        for geo_id in geographies:
            geo = geography_dao.get_by_id(geo_id)
            if geo: # Maybe unneccesary security check
                query.geographies.append(geo)
                scrapingquery_dao.save(query)
                return ResponseBody(success_message='Query succesfully created')
        return ResponseBody(error_message='Query could not be created')
    
    @request_handler
    def update_query(self, id, name, age, category, geographies, criterias):
        
        user_id = user_dao.get_user_attr('id')
        query = scrapingquery_dao.get_first_where(id=id, user_id=user_id)
        
        if query:
            query.name, query.age, query.category, query.criterias = name, age, category, criterias
            
            existing_geo_relations = [geo.id for geo in query.geographies] 

            #Add
            for geo_id in geographies:
                if geo_id not in existing_geo_relations:
                    geo = geography_dao.get_by_id(geo_id)
                    if geo: # Maybe unneccesary security check
                        query.geographies.append(geo)
            #Remove
            for geo_id in existing_geo_relations:
                if geo_id not in geographies:
                    geo = geography_dao.get_by_id(geo_id)
                    if geo:
                        query.geographies.remove(geo)
        
                      
            scrapingquery_dao.save(query)
            return ResponseBody(success_message='Query updated successfully')
        return ResponseBody(error_message='Query could not be updated')
                
    @request_handler
    def get_query(self, id):
        query = scrapingquery_dao.get_by_id(id)
        return ResponseBody(requested_obj={'id': query.id, 'name': query.name, 'age': query.age,
                             'category': query.category, 
                             'criterias': str(query.criterias).split(','),
                             'geographies': [geo.id for geo in query.geographies]})


class JobpostService():

    def exectue_query(self, scrapingquery_id):
        
        user_id = user_dao.get_user_attr('id')
        query = scrapingquery_dao.get_first_where(id=scrapingquery_id, user_id=user_id)
        
        if query:
            # Get New jobposts
            new_jobposts_dict = webscraper(query.to_dict())
            # Get Existing link of user and query
            existing_jobposts = jobpost_dao.get_all_where(scrapingquery_id=scrapingquery_id)

            relevant_jobposts = self.__execute_query_protocols(existing_jobposts, new_jobposts_dict, scrapingquery_id)  
            relevant_jobposts_jsonformat = [jobpost.to_dict() for jobpost in relevant_jobposts]
            return ResponseBody(requested_obj=relevant_jobposts_jsonformat)
        else: 
            return ResponseBody(error_message="Choose a query first(go to Queries to create one if tyou haven't)")
        
    def set_jobpost_status_to_removed(self, jobpost_id):
        jobpost = jobpost_dao.get_first_where(id=jobpost_id)
        if jobpost:
            jobpost_dao.update_where(jobpost_id, status=1) 
            return ResponseBody(requested_obj=jobpost.id)
        else:
            return ResponseBody(error_message="Illegal")


    def __execute_query_protocols(self, existing_jobposts, new_jobposts_dict, scrapingquery_id) -> list:
        
        """_summary_: 1. Deletes outdated and irrelevant jobposts that are associated with query.
                      2. Deletes jobpost from db that are associated with query, and are either outdated or irrelevant.
                      3. Saves new Jobposts, if they are not part of jobposts that are already persisted for query - 
                      and are not found to be outdated/irrelevant.
                      4. Creates list (old_jobpost_relevant) of jobpost from old persisted jobposts -
                      where offline status (attr status !=0) are not members.
                      4. Combines the old_jobpost_relevant and new jobposts and returns them.
                      old jobposts (2) and new non-copy jobposts (3)
                      
        

        Returns:
            _type_: list of Jobpost
            Should this not be dict of something?
        """

        # Existing links to dict
        existing_jobposts_dict = {jobpost.unique_identifier: jobpost for jobpost in existing_jobposts}
        
        # DELETE
        old_persisting_jobposts = self.__delete_protocol(existing_jobposts_dict, new_jobposts_dict)
        
        # SAVE 
        new_persisted_jobposts = self.__save_protocol(new_jobposts_dict, existing_jobposts_dict, scrapingquery_id)
        
        old_jobpost_relevant = [jobpost for jobpost in old_persisting_jobposts if jobpost.status==0]
        
        # concat of two lists of models
        relevant_jobposts = new_persisted_jobposts + old_jobpost_relevant 
        
        return relevant_jobposts
    
    def __delete_protocol(self, existing_jobposts_dict, new_jobposts_dict) -> list:
        """_summary_

        Args:
            existing_jobposts_dict (dict): _description_
            new_jobposts_dict (dict): _description_

        Returns:
            list: of Jobpost
        """
        
        #Difference
        outdated_jobposts_set = (existing_jobposts_dict.keys() - new_jobposts_dict.keys())
        
        # DICT OF JOBPOSTS TO DELETE FROM EXISTING DICTS
        existing_jobposts_to_delete = dict({})
        # DICT OF JOBPOSTS TO RETURN TO VIEW
        persisting_jobposts = dict({})

        for key,val in existing_jobposts_dict.items():
            if key in outdated_jobposts_set:
                existing_jobposts_to_delete[key] = val 
            else:
                persisting_jobposts[key] = val
                
        # DELETE OUTDATED and IRRELEVANT            
        if existing_jobposts_to_delete:
            jobpost_dao.delete_all(list(existing_jobposts_to_delete.values()))        
                
        return list(persisting_jobposts.values())
                
                   
    def __save_protocol(self, new_jobposts_dict, existing_jobposts_dict, scrapingquery_id):
        
        # REMOVE LINKS FROM NEW_LINKS THAT ARE ALREADY IN EXISTING, & is intersecting with old that shall be persisted
        new_jobposts_to_save = {key:val for (key, val) in new_jobposts_dict.items() if key in 
                                (new_jobposts_dict.keys() - (new_jobposts_dict.keys() & existing_jobposts_dict.keys()) )} 
        
        # SAVE NEW LINKS
        if new_jobposts_to_save:
            new_persisted_jobposts = [jobpost_dao.create_new(unique_identifier=jobpost[0], url=jobpost[1], 
                                    scrapingquery_id=scrapingquery_id, status=0) for jobpost in new_jobposts_to_save.items()] 
            jobpost_dao.save_all(new_persisted_jobposts)
            
            return new_persisted_jobposts
        else: 
            return []
            
        # ALL NEW STUFF TO SAVE 
    

class CLService():
    
    @request_handler
    def create_prompt(self, data:dict):
        job_info = self.__translate_to_(data['job_info'], dest_language='en')
        full_name = user_service.get_real_name()
        education = user_service.get_education()
        prompt = self.__construnct_prompt(motivations=data['motivations'], skills=data['skills'],
                                          full_name=full_name, job_info=job_info, education=education)
        return ResponseBody(requested_obj=prompt)
    
    @request_handler
    def create_cl(self, prompt, temperature, top_p, frequency_penalty, presence_penalty):
        #Generate cover letters
        footer_text =" ".join("""This application was created by cover-letter automation software that utilizes webscraping, 
        data-mining, machine learning and other exciting technologies (created by myself of course).
        Link to my Github for those of you who wants to check it out: 'github link'
        """.split())
        cl_english = create_cover_letter(prompt, temperature, top_p, frequency_penalty, presence_penalty)
        cl = cl_english + '\t' + footer_text
        cl_container = [cl, self.__translate_to_(cl, dest_language='da')]
        return ResponseBody(requested_obj=cl_container)
    
    
    def __construnct_prompt(self, motivations, skills, full_name, job_info, education):

        first_name = full_name.split(' ')[0]
        motivations = ', '.join([dictionary['text'] for dictionary in motivations])
        skills = ', '.join([dictionary['text'] for dictionary in skills])

        prompt = """
        Based on a job post and information on an applicant, 
        write a truthful cover letter where you do not lie about the skills or your educational background. 
        This is the job post: {job_info}. And this is the author of this application: 
        (Name of applicant: {full_name}, Skills: {skills}. I am motivated by 
        {motivations}. I have an educational background in: {education}.
        """.format(job_info=job_info, full_name=full_name, 
                    skills=skills, first_name=first_name, motivations=motivations, education=education)
        # Remove newlines and add newline at end.
        prompt = " ".join(prompt.split())+"\n"
        return prompt
    
    def __translate_to_(self, cl_text, dest_language):
        
        trans = Translator()
        if len(cl_text) > 4000:
            step = 4000
            chunks = [cl_text[i:i+step] for i in range(0, len(cl_text), step)]
            #Translate text chunk for chunk, as google api will block you otherwise.
            return ' '.join([trans.translate(chunk, dest=dest_language).text for chunk in chunks])
        else:
            return trans.translate(cl_text, dest=dest_language).text


    
    
cl_service = CLService()
jobpost_service = JobpostService()
scrapingquery_service = ScrapingQueryService()    
competence_service = CompetenceService()      
user_service = UserService()
