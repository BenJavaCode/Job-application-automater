from ..persistence.dao import user_dao, competenceset_dao, competence_dao
from .service_handlers import request_handler, responsebody

# Decoupling from frontend implementation, so that they return general object types


@request_handler
def get_sets():
    user_id = user_dao.get_user_attr('id')
    responsebody = responsebody(success=True, payload=[_set for _set in competenceset_dao.get_all_where(user_id=user_id)])
    # [(s.id, s.name) for s in competenceset_dao.get_all_where(user_id=user_id)]
    return responsebody

@request_handler
def get_sets_by_type(set_type, json_format=True):
    user_id = user_dao.get_user_attr('id')
    competencesets = competenceset_dao.get_all_where(user_id=user_id, set_type=set_type)
    return responsebody(success=True, payload=competencesets)
    """ 
    if json_format:
        initial_option = [{'id':-1, 'name':'--Select Set--'}]
        sets = [{'id': competenceset.id, 'name': competenceset.name } for competenceset in competencesets]
    else: 
        initial_option = [(-1, '--Select Set--')]
        sets = [(competenceset.id, competenceset.name ) for competenceset in competencesets]
    """

@request_handler
def create_set(name, set_type):  
    user_id = user_dao.get_user_attr('id')
    competence_set = competenceset_dao.create_new(user_id=user_id, name=name, set_type=set_type)
    competenceset_dao.save(competence_set)
    return responsebody(success=True, message_text=f'Set with name {name} succesfully created', payload=competence_set)
    #return ResponseBody(requested_obj={'id': competence_set.id, 'name': competence_set.name})

@request_handler
def delete_competence_set(set_id):
    user_id = user_dao.get_user_attr('id')
    if competenceset_dao.get_first_where(user_id=user_id, id=set_id):
        competenceset_dao.delete_by_id(set_id)
        return responsebody(success=True, message_text='Successfully deleted')
    else: 
        return responsebody(success=False, message_text='Not Allowed, bad user!')

# /SETS

# Competences
@request_handler
def create_competence(text, competenceset_id):
    if competenceset_dao.get_first_where(id=competenceset_id):
        competence = competence_dao.create_new(text=text, competenceset_id=competenceset_id)
        competence_dao.save(competence)
        return responsebody(success=True, payload=competence)
        #return ResponseBody(requested_obj={'id':competence.id, 'text': competence.text})
    else: 
        return responsebody(success=False, message_text='You need to choose first')


@request_handler
def delete_competence(id, competenceset_id):
    user_id = user_dao.get_user_attr('id')
    if competenceset_dao.get_first_where(user_id=user_id, id=competenceset_id):
        if competence_dao.get_first_where(id=id, competenceset_id=competenceset_id):
            competence_dao.delete_by_id(id)
            return responsebody(success=True, payload=id)
    return responsebody(success=False, message_text='Not Allowed, bad user!')


@request_handler 
def get_competences_by_set_id(competenceset_id): 
    competences = competence_dao.get_all_where(competenceset_id=competenceset_id)
    """ 
    response = ResponseBody( requested_obj = 
                            [{'id': competence.id, 'text': competence.text } for competence in competences])
    """
    return responsebody(success=True, payload=competences)