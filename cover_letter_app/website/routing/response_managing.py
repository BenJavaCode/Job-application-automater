from flask import flash
from ..services.scraping_query_service import get_queries

def populate_query_selector(query_selector_form):
    responsebody = get_queries()
    choices = [(query.id, query.name) for query in responsebody['payload']]
    query_selector_form.options.choices.extend(choices)

# For flashing messages on synchronous callbacks
def synchronous_flash(responsebody):
    flash(responsebody['message']['message_text'], category=responsebody['message']['category'])

   
