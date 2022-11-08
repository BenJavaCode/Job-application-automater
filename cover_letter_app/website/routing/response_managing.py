from flask import flash
from ..services.scraping_query_service import get_queries

def populate_query_selector(query_selector_form):
    responsebody = get_queries()
    choices = [(query.id, query.name) for query in responsebody['payload']]
    query_selector_form.options.choices.extend(choices)

# For flashing messages on synchronous callbacks
def synchronous_flash(responsebody):
    flash(responsebody['message']['message_text'], category=responsebody['message']['category'])

    

def manage_response(responsebody):
    """_summary_:
       Manages the ResponseBody returned from services. Used by routing.
       It is the responsibility of the routing function, to know how to handle the return object of this function.

    Args:
        responsebody (_type_): ResponseBody obj.

    Returns:
        If the request was succesfully proccessed the return will be True. 
        Else it will be false.
        If the ResponseBody of the request includes a response_obj, then it will be returned (And thus still evaluate to True).
    """
    #Successes, Return evaluates to True
    if responsebody.success_message is not None:
        flash(responsebody.success_message, category='success')
        return True
            
    elif responsebody.requested_obj is not None:
        return responsebody.requested_obj
    
    #Errors, Return is False
    elif responsebody.error_message is not None:
        flash(responsebody.error_message, category='error')
        
    
    elif responsebody.exception is not None:
        flash('An error occured, try again later', category='error')
        
    
    return False

   
