"""_summary_:
    Handler functions and return value wrappers used by service layer.
"""

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
        

def responsebody(success:bool, message_text='', payload=''):
    """_summary_:
        Constructs a responsebody, which is the standardized data structure used for all communication with 
        routing functions. 
    Args:
        message_text = any string of type str.
        success = type: bool. True for success False for error.
        payload = type: can be annything. Optional payload used by routing function. Shall be a dictionary object.
    """
    message_category = 'success' if success else 'error'
    return {'message': {'message_text': message_text, 'category': message_category}, 
            'payload': payload}


def request_handler(func):
    """_summary_:
        Decorator/adapter used for all service functions, that are not private (that are used directly by views).
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
            return responsebody(message_text='An error occured, try again later', success=False)
    return handle_outcome

