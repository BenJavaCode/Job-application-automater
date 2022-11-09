"""_summary_:
    Handler functions and return value wrappers used by service layer.
"""  

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

