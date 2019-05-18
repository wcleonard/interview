基于Scrapy框架的图片爬虫项目


分析网页结构

    1.爬取的目标网站: https://image.so.com
    
    2.打开浏览器开发者工具会呈现许多Ajax请求返回JSON格式数据
    
    3.观察请求参数会发现只有一个参数sn(偏移量)一直在变化


解析网页

  1.定义Item(items.py)
    
    class Images360Item(scrapy.Item):
        # define the fields for your item here like:
        collection = table = 'images'
        id = scrapy.Field()
        url = scrapy.Field()
        title = scrapy.Field()
        thumb = scrapy.Field()
  

  2.提取信息(images.py)

    def parse(self, response):
        result = json.loads(response.text)
        print(result)
        for image in result.get('list'):
            item = Images360Item()
            item['id'] = image.get('imageid')
            item['url'] = image.get('qhimg_url')
            item['title'] = image.get('group_title')
            item['thumb'] = image.get('qhimg_thumb_url')
            yield item

  3.简单的数据清洗

    def parse_title(self, title):
        if re.findall('/', title):
            title = title.replace('/', '')
        if re.findall(':', title):
            title = title.replace(':', '')
        return title
  
  4.使用user_agent模仿浏览器访问(middlewares.py)
  
    class RandomUserAgentMiddleware():
        def __init__(self):
            self.user_agents = [
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
                'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/3.1)',
                'Mozilla/5.0 (iPod; U; CPU iPhone OS 4_0 like Mac OS X; gd-GB) AppleWebKit/535.25.4 (KHTML, like Gecko) Version/4.0.5 Mobile/8B114 Safari/6535.25.4',
            ]
        def process_request(self, request, spider):
            request.headers['User-Agent'] = random.choice(self.user_agents)  
         
  5.使用代理(middlewares.py)

    class ProxyMiddleware():
        def __init__(self, proxy_url):
            self.proxy_url = proxy_url
    
        def get_random_proxy(self):
            try:
                response = requests.get(self.proxy_url)
                if response.status_code == 200:
                    proxy = response.text
                    return proxy
            except requests.ConnectionError:
                return False
    
        def process_request(self, request, spider):
            if request.meta.get('retry_times'):
                proxy = self.get_random_proxy()
                if proxy:
                    uri = 'https://{proxy}'.format(proxy=proxy)
                    request.meta['proxy'] = uri
    
        @classmethod
        def from_crawler(cls, crawler):
            settings = crawler.settings
            return cls(
                proxy_url=settings.get('PROXY_URL')
            )

存储信息(pipelines.py)

  (1)保存到MySQL数据库

    class MongoPipeline(object):
        def __init__(self, mongo_uri, mongo_db):
            self.mongo_uri = mongo_uri
            self.mongo_db = mongo_db
    
        @classmethod
        def from_crawler(cls, crawler):
            return cls(
                mongo_uri=crawler.settings.get('MONGO_URI'),
                mongo_db=crawler.settings.get('MONGO_DB')
            )
    
        def open_spider(self, spider):
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
    
        def process_item(self, item, spider):
            self.db[item.collection].insert(dict(item))
            return item
    
        def close_spider(self, spider):
            self.client.close()
    
  (2)保存到MongoDB数据库

    class MysqlPipeline():
        def __init__(self, host, database, user, password, port):
            self.host = host
            self.database = database
            self.user = user
            self.password = password
            self.port = port
    
        @classmethod
        def from_crawler(cls, crawler):
            return cls(
                host=crawler.settings.get('MYSQL_HOST'),
                database=crawler.settings.get('MYSQL_DATABASE'),
                user=crawler.settings.get('MYSQL_USER'),
                password=crawler.settings.get('MYSQL_PASSWORD'),
                port=crawler.settings.get('MYSQL_PORT'),
            )
    
        def open_spider(self, spider):
            self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
            self.cursor = self.db.cursor()
    
        def close_spider(self, spider):
            self.db.close()
    
        def process_item(self, item, spider):
            data = dict(item)
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
            return item
            
  (3)保存到本地

    class ImagePipeline(ImagesPipeline):
        def file_path(self, request, response=None, info=None):
            url = request.url
            file_name = url.split('/')[-1]
            return file_name
    
        def item_completed(self, results, item, info):
            image_paths = [x['path'] for ok, x in results if ok]
            if not image_paths:
                raise DropItem('Image Downloaded Failed')
            return item
    
        def get_media_requests(self, item, info):
            yield Request(item['url'])
