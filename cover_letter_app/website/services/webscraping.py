import requests
from lxml.html import fromstring   


## Utils webscraper to be used by Service    
class WebScraper():
    """
    Multiple scrapers can be sequentially executed with a query and there results can be aggregated into a dict(set)
    So that only unique results are returned(in theory).
    """
    
    def __init__ (self, scrapers: list):
        self.scrapers = scrapers
    
    def __call__(self, query):
        result_dict = {}
        for scraper in self.scrapers:
            result_dict.update(scraper.execute_query(query))
        return result_dict   
    
                               

class JobindexScraper2():
    # JobindexScraper 1 was made with selenium, and i also have a scraper for ofir and jobnet if enyone is interested.
    # I however found that almost all jobs are posted on jobindex, so scraping the other sites are somewhat a waste of time

    geocodes = {'Storkøbenhavn':'15182', 'Nordsjælland':'15187', 'Sjælland':'4', 'Fyn':'15179',
               'Nordjylland':'3','Midtjylland':'2','Sydjylland':'15180', 'Bornholm':'15',
               'Skåne':'16149', 'Grønland':'15271','Færøerne':'15799','Udlandet':'15185','Danmark':'1221'}
    
    categorycodes = {"Informationsteknologi":"it", "Ingeniør":"ingenioer", "Ledelse":"ledelse", "Handel og service":"handel",
                     "Salg og kommunikation":"salg", "Undervisning":"undervisning", "Kontor og økonomi":"kontor",
                     "Social og sundhed":"social", "Øvrige stillinger":"oevrige"}
    
    baseurl = "https://www.jobindex.dk/jobsoegning/"
                               
    agecodes = {-1:'', 0:'1', 1: '2', 2: '3', 3:'4', 4:'5', 5:'6', 6:'7', 7:'14', 8:'30'}

    
    
 
    def execute_query(self, query) -> dict:
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
    
            
webscraper = WebScraper([JobindexScraper2()])
#jobposts = scraper(query={'category':'Informationsteknologi','age':7,'criterias':'python,java', 'geographies':['Storkøbenhavn', 'Grønland', 'Bornholm']})
#len(jobposts), jobposts