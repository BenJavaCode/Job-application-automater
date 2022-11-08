from ..persistence.dao import user_dao, scrapingquery_dao, jobpost_dao
from .service_handlers import request_handler, responsebody

import requests
from lxml.html import fromstring   

## Webscraper object, that can be extended with more targets    
class WebScraper:
    """
    Multiple scrapers can be sequentially executed with a query and the results can be aggregated into a dict(set)
    So that only unique results are returned(in theory).
    """
    
    def __init__ (self, scrapers: list):
        self.scrapers = scrapers
    
    def __call__(self, query):
        result_dict = {}
        for scraper in self.scrapers:
            result_dict.update(scraper.execute_query_(query))
        return result_dict   
    
                               

class JobindexScraper2:
    # JobindexScraper 1 was made with selenium, and i also have a scraper for ofir and jobnet if anyone is interested.
    # I however found that almost all jobs are posted on jobindex, so scraping the other sites are somewhat a waste of time.

    # Translationdict's from this environment to jobindex.
    geocodes = {'Storkøbenhavn':'15182', 'Nordsjælland':'15187', 'Sjælland':'4', 'Fyn':'15179',
               'Nordjylland':'3','Midtjylland':'2','Sydjylland':'15180', 'Bornholm':'15',
               'Skåne':'16149', 'Grønland':'15271','Færøerne':'15799','Udlandet':'15185','Danmark':'1221'}
    
    categorycodes = {"Informationsteknologi":"it", "Ingeniør":"ingenioer", "Ledelse":"ledelse", "Handel og service":"handel",
                     "Salg og kommunikation":"salg", "Undervisning":"undervisning", "Kontor og økonomi":"kontor",
                     "Social og sundhed":"social", "Øvrige stillinger":"oevrige"}
    
    agecodes = {-1:'', 0:'1', 1: '2', 2: '3', 3:'4', 4:'5', 5:'6', 6:'7', 7:'14', 8:'30'}

    baseurl = "https://www.jobindex.dk/jobsoegning/"
                               

    def execute_query_(self, query) -> dict:
        url_parts =  self.__construct_request_url(query)
        return self.__gather_jobpost_info(url_parts)
  
    def __gather_jobpost_info(self, url_parts) -> dict:
        
        resp = requests.get(url_parts[0] + url_parts[1])
        DOM_model = fromstring(resp.text)
        jobposts = dict({})
        num_pages = None
        try:
            num_pages = int(DOM_model.xpath("//*[@id='result_list_box']/div[2]/nav/ul/li[last()-1]/a/text()")[0])
        except:
            num_pages = 1
        for jobpost_subdict in self.__extract_jobinfo(url_parts, num_pages):
            jobposts.update(jobpost_subdict)
        
        return jobposts

            
    def __extract_jobinfo(self, url_parts, num_pages):
        
        for current_page_num in range(1, num_pages+1):
            resp = requests.get(url_parts[0] + f"page={current_page_num}&" + url_parts[1])
            print(url_parts[0] + f"page={current_page_num}&" + url_parts[1])
            if resp.status_code == 200:
                DOM_model = fromstring(resp.text)

                paid_job = {", ".join([title, company]): link
                                for (title, company, link) in 
                                zip(DOM_model.xpath("//div[@class='PaidJob-inner']/a/b/text()"),
                                  DOM_model.xpath("//div[@class='PaidJob-inner']/p[1]/a[1]/b/text()"),
                                  DOM_model.xpath("//div[@class='PaidJob-inner']/a/b/../@href"))
                        }
                robot_job = {", ".join([title, company]): link
                                        for (title, company, link) in 
                                          zip(DOM_model.xpath("//div[@class='jix_robotjob-inner']//a[1]/strong/text()"), 
                                              DOM_model.xpath("//div[@class='jix_robotjob-inner']//b[1]/text()"),
                                              DOM_model.xpath("//div[@class='jix_robotjob-inner']//a[1]/@href"))
                                }

                paid_job.update(robot_job)
                yield paid_job
            
    
    def __construct_request_url(self, query) -> list:
        # https://www.jobindex.dk/jobsoegning/it?geoareaid=15182&geoareaid=4&q=python+java
        # baseurl/ CATEGORY ? geoareaid=GEOCODE & geoareaid=GEOCODE & q=CRITERIA_ITEMS_SEPERATED_BY_+
        url_bulk = self.baseurl
        criteria_ext = ''
        
        if query['category'] != 'none':
            url_bulk += self.categorycodes[query['category']]
        url_bulk += '?'
        
        if query['geographies']:
            for geo in query['geographies']:
                url_bulk += f"geoareaid={self.geocodes[geo]}&"
                               
        if query['age'] != -1:
            url_bulk += f"jobage={self.agecodes[query['age']]}&"
                
        if query['criterias']:
            criteria_ext = f"q={str(query['criterias']).replace(',', '+')}"
            
        return [url_bulk, criteria_ext]
    


@request_handler
def execute_query(scrapingquery_id):
    
    user_id = user_dao.get_user_attr('id')
    query = scrapingquery_dao.get_first_where(id=scrapingquery_id, user_id=user_id)
    webscraper = WebScraper([JobindexScraper2()])

    if query:
        # Get New jobposts
        new_jobposts_dict = webscraper(query.to_dict())
        # Get Existing link of user and query
        existing_jobposts = jobpost_dao.get_all_where(scrapingquery_id=scrapingquery_id)

        relevant_jobposts = __execute_query_protocols(existing_jobposts, new_jobposts_dict, scrapingquery_id)  
        relevant_jobposts_jsonformat = [jobpost.to_dict() for jobpost in relevant_jobposts]
        return responsebody(success=True, payload=relevant_jobposts_jsonformat)
    else: 
        return responsebody(success=False, message_text="Choose a query first(go to Queries to create one if tyou haven't)")
    
@request_handler
def set_jobpost_status_to_removed(jobpost_id):
    jobpost = jobpost_dao.get_first_where(id=jobpost_id)
    if jobpost:
        jobpost_dao.update_where(jobpost_id, status=1) 
        return responsebody(success=True, payload=jobpost.id)
    else:
        return responsebody(success=False, message_text="Illegal")


def __execute_query_protocols(existing_jobposts, new_jobposts_dict, scrapingquery_id) -> list:
    
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
    old_persisting_jobposts = __delete_protocol(existing_jobposts_dict, new_jobposts_dict)
    # SAVE 
    new_persisted_jobposts = __save_protocol(new_jobposts_dict, existing_jobposts_dict, scrapingquery_id)
    # Old jobpost that has persisted
    old_jobpost_relevant = [jobpost for jobpost in old_persisting_jobposts if jobpost.status==0]
    # concat of two lists of models
    relevant_jobposts = new_persisted_jobposts + old_jobpost_relevant 
    
    return relevant_jobposts

def __delete_protocol(existing_jobposts_dict, new_jobposts_dict) -> list:
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
            
                
def __save_protocol(new_jobposts_dict, existing_jobposts_dict, scrapingquery_id):
    
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
        
