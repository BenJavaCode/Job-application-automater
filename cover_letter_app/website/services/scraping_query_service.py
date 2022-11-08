from ..persistence.dao import user_dao, scrapingquery_dao, geography_dao
from .service_handlers import request_handler, responsebody

"""_summary_:
Scraping query services, that either query or manipulate data in the Scrapingquery object model.
Used by routing layer. 
"""

@request_handler
def create_query(name, age, category, geographies, criterias):
    
    user_id = user_dao.get_user_attr('id')
    query = scrapingquery_dao.create_new(user_id=user_id, name=name, age=age, category=category, criterias=criterias)
        
    for geo_id in geographies:
        geo = geography_dao.get_by_id(geo_id)
        if geo: # Maybe unneccesary security check
            query.geographies.append(geo)
    scrapingquery_dao.save(query)
    
    return responsebody(success=True, message_text='Query succesfully created')

@request_handler
def update_query(id, name, age, category, geographies, criterias):
    
    user_id = user_dao.get_user_attr('id')
    query = scrapingquery_dao.get_first_where(id=id, user_id=user_id)
    
    if query:
        query.name, query.age, query.category, query.criterias = name, age, category, criterias
        existing_geo_relations = [geo.id for geo in query.geographies] 
        
        # Remove geo relation if part of new geo relations (manipulates query)
        __remove_obsolete_geo_relation(query, geographies, existing_geo_relations)
        # Add geo relationship if not already exists (manipulates query)
        __add_new_geo_relation(query, geographies, existing_geo_relations)
        scrapingquery_dao.save(query)
        
        return responsebody(success=True, message_text='Query updated successfully')
    return responsebody(success=False, message_text='Query could not be updated')
      
            
def __remove_obsolete_geo_relation(query, geographies, existing_geo_relations):
    for geo_id in existing_geo_relations:
        if geo_id not in geographies:
            geo = geography_dao.get_by_id(geo_id)
            if geo:
                query.geographies.remove(geo)


def __add_new_geo_relation(query, geographies, existing_geo_relations):
    for geo_id in geographies:
        if geo_id not in existing_geo_relations:
            geo = geography_dao.get_by_id(geo_id)
            if geo: # Maybe unneccesary security check
                query.geographies.append(geo)

@request_handler
def get_queries():
    user_id = user_dao.get_user_attr('id')
    queries = scrapingquery_dao.get_all_where(user_id=user_id)
    return responsebody(success=True, payload=queries)
    #return ResponseBody(requested_obj = initial_option + [(query.id, query.name) for query in queries])

@request_handler
def get_query(id):
    query = scrapingquery_dao.get_by_id(id)
    return responsebody(success=True, payload=query)
    """ 
    return ResponseBody(requested_obj={'id': query.id, 
                                       'name': query.name, 
                                       'age': query.age,
                                       'category': query.category, 
                                       'criterias': str(query.criterias).split(','),
                                       'geographies': [geo.id for geo in query.geographies]
                                       })
    """


