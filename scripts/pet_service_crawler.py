"""
Amap Pet Service Crawler - Complete Version
===========================================

Features:
1. Collect pet service business data from all 34 provincial-level regions in China
2. Support Guangdong-only crawl or national crawl
3. Automatic API rate limiting
4. Data deduplication and formatted storage
5. Detailed logging and statistics report

Author: Database Management Systems Project Team
Date: April 2026
"""

import requests
import json
import csv
import time
import logging
import os
from datetime import datetime


class AmapPetServiceCrawler:
    """Core crawler class for Amap pet service data collection"""
    
    def __init__(self, api_key):
        """Initialize crawler with API key"""
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com/v3/place/text"
        self.pet_keywords = ["宠物服务", "宠物医院", "宠物美容", "宠物用品", "宠物寄养"]
        self.collected_data = []
        self.processed_ids = set()
        self.api_call_count = 0
        self.last_call_time = 0
    
    def search_pet_services(self, city, keyword, page=1, offset=25):
        """Call Amap API to search pet services"""
        self.api_call_count += 1
        
        if self.api_call_count % 100 == 0:
            logging.info(f"API Call Stats: {self.api_call_count} calls made")
        
        wait_time = 1.5
        current_time = time.time()
        if current_time - self.last_call_time < wait_time:
            time.sleep(wait_time - (current_time - self.last_call_time))
        self.last_call_time = time.time()
        
        params = {
            "key": self.api_key,
            "keywords": keyword,
            "city": city,
            "extensions": "all",
            "page": page,
            "offset": offset,
            "output": "json"
        }
        
        for retry in range(3):
            try:
                logging.info(f"Calling API: city={city}, keyword={keyword}, page={page}")
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1":
                    count = data.get("count", "0")
                    logging.info(f"API response successful: {count} records")
                    return data
                else:
                    error_info = data.get('info', 'Unknown error')
                    if 'CUQPS_HAS_EXCEEDED_THE_LIMIT' in error_info:
                        logging.warning("API rate limit exceeded, waiting 60 seconds...")
                        time.sleep(60)
                        continue
                    logging.error(f"API error: {error_info}")
                    return None
            except requests.RequestException as e:
                logging.error(f"Request failed (retry {retry+1}/3): {e}")
                time.sleep(2)
                continue
        
        return None
    
    def process_business_data(self, business):
        """Process and deduplicate business data"""
        business_id = business.get("id")
        
        if business_id in self.processed_ids:
            return None
        
        self.processed_ids.add(business_id)
        
        business_info = {
            "id": business_id,
            "name": business.get("name"),
            "address": business.get("address"),
            "city": business.get("cityname"),
            "district": business.get("adname"),
            "phone": business.get("tel", ""),
            "rating": business.get("biz_ext", {}).get("rating", ""),
            "location": business.get("location"),
            "type": business.get("type"),
            "biz_type": business.get("biz_type"),
            "open_time": business.get("biz_ext", {}).get("open_time", ""),
            "cost": business.get("biz_ext", {}).get("cost", "")
        }
        
        return business_info
    
    def crawl_city(self, city):
        """Crawl all pet services in a specific city"""
        logging.info(f"Starting crawl for city: {city}")
        
        for keyword in self.pet_keywords:
            logging.info(f"Searching with keyword: {keyword}")
            page = 1
            has_more = True
            
            while has_more:
                data = self.search_pet_services(city, keyword, page)
                
                if not data:
                    logging.warning(f"Failed to get page {page} for {city} {keyword}")
                    time.sleep(2)
                    continue
                
                pois = data.get("pois", [])
                
                if not pois:
                    has_more = False
                    logging.info(f"No more data for {city} {keyword}")
                    break
                
                for poi in pois:
                    business_info = self.process_business_data(poi)
                    if business_info:
                        self.collected_data.append(business_info)
                
                count = int(data.get("count", 0))
                total_pages = (count + 24) // 25
                
                if page >= total_pages:
                    has_more = False
                else:
                    page += 1
                    time.sleep(1.2)
    
    def save_to_json(self, filename):
        """Save data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logging.error(f"Failed to save JSON: {e}")
            return False
    
    def save_to_csv(self, filename):
        """Save data to CSV file"""
        if not self.collected_data:
            logging.warning("No data to save")
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = list(self.collected_data[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.collected_data:
                    writer.writerow(item)
            logging.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logging.error(f"Failed to save CSV: {e}")
            return False
    
    def reset(self):
        """Reset crawler state for new crawl"""
        self.collected_data = []
        self.processed_ids = set()


class CrawlerManager:
    """Manager class for coordinating national crawl tasks"""
    
    def __init__(self, api_key, output_dir="pet_services_data"):
        """Initialize manager with API key and output directory"""
        self.api_key = api_key
        self.output_dir = output_dir
        self.crawler = AmapPetServiceCrawler(api_key)
        
        self.national_provinces = {
            "North China": ["北京市", "天津市", "河北省", "山西省", "内蒙古自治区"],
            "Northeast China": ["辽宁省", "吉林省", "黑龙江省"],
            "East China": ["上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省"],
            "Central China": ["河南省", "湖北省", "湖南省"],
            "South China": ["广东省", "广西壮族自治区", "海南省", "重庆市", "四川省", "贵州省", "云南省", "西藏自治区"],
            "Northwest China": ["陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区"],
            "Hong Kong, Macao, Taiwan": ["香港特别行政区", "澳门特别行政区", "台湾省"]
        }
        
        self.crawl_stats = {}
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_province_cities(self, province):
        """Get list of cities for a province"""
        if province in ["北京市", "上海市", "重庆市", "天津市"]:
            return [province]
        
        province_cities = {
            "内蒙古自治区": ["呼和浩特市", "包头市", "乌海市", "赤峰市", "通辽市", "鄂尔多斯市", "呼伦贝尔市", "巴彦淖尔市", "乌兰察布市"],
            "黑龙江省": ["哈尔滨市", "齐齐哈尔市", "鸡西市", "鹤岗市", "双鸭山市", "大庆市", "伊春市", "佳木斯市", "七台河市", "牡丹江市", "黑河市", "绥化市"],
            "吉林省": ["长春市", "吉林市", "四平市", "辽源市", "通化市", "白山市", "松原市", "白城市"],
            "辽宁省": ["沈阳市", "大连市", "鞍山市", "抚顺市", "本溪市", "丹东市", "锦州市", "营口市", "阜新市", "辽阳市", "盘锦市", "铁岭市", "朝阳市", "葫芦岛市"],
            "河北省": ["石家庄市", "唐山市", "秦皇岛市", "邯郸市", "邢台市", "保定市", "张家口市", "承德市", "沧州市", "廊坊市", "衡水市"],
            "山西省": ["太原市", "大同市", "阳泉市", "长治市", "晋城市", "朔州市", "晋中市", "运城市", "忻州市", "临汾市", "吕梁市"],
            "江苏省": ["南京市", "无锡市", "徐州市", "常州市", "苏州市", "南通市", "连云港市", "淮安市", "盐城市", "扬州市", "镇江市", "泰州市", "宿迁市"],
            "浙江省": ["杭州市", "宁波市", "温州市", "嘉兴市", "湖州市", "绍兴市", "金华市", "衢州市", "舟山市", "台州市", "丽水市"],
            "安徽省": ["合肥市", "芜湖市", "蚌埠市", "淮南市", "马鞍山市", "淮北市", "铜陵市", "安庆市", "黄山市", "滁州市", "阜阳市", "宿州市", "六安市", "亳州市", "池州市", "宣城市"],
            "福建省": ["福州市", "厦门市", "莆田市", "三明市", "泉州市", "漳州市", "南平市", "龙岩市", "宁德市"],
            "江西省": ["南昌市", "景德镇市", "萍乡市", "九江市", "新余市", "鹰潭市", "赣州市", "吉安市", "宜春市", "抚州市", "上饶市"],
            "山东省": ["济南市", "青岛市", "淄博市", "枣庄市", "东营市", "烟台市", "潍坊市", "济宁市", "泰安市", "威海市", "日照市", "临沂市", "德州市", "聊城市", "滨州市", "菏泽市"],
            "河南省": ["郑州市", "开封市", "洛阳市", "平顶山市", "安阳市", "鹤壁市", "新乡市", "焦作市", "濮阳市", "许昌市", "漯河市", "三门峡市", "南阳市", "商丘市", "信阳市", "周口市", "驻马店市"],
            "湖北省": ["武汉市", "黄石市", "十堰市", "宜昌市", "襄阳市", "鄂州市", "荆门市", "孝感市", "荆州市", "黄冈市", "咸宁市", "随州市", "恩施土家族苗族自治州"],
            "湖南省": ["长沙市", "株洲市", "湘潭市", "衡阳市", "邵阳市", "岳阳市", "常德市", "张家界市", "益阳市", "郴州市", "永州市", "怀化市", "娄底市", "湘西土家族苗族自治州"],
            "广东省": ["广州市", "深圳市", "珠海市", "汕头市", "佛山市", "韶关市", "湛江市", "肇庆市", "江门市", "茂名市", "惠州市", "梅州市", "汕尾市", "河源市", "阳江市", "清远市", "东莞市", "中山市", "潮州市", "揭阳市", "云浮市"],
            "广西壮族自治区": ["南宁市", "柳州市", "桂林市", "梧州市", "北海市", "防城港市", "钦州市", "贵港市", "玉林市", "百色市", "贺州市", "河池市", "来宾市", "崇左市"],
            "海南省": ["海口市", "三亚市", "三沙市", "儋州市"],
            "四川省": ["成都市", "自贡市", "攀枝花市", "泸州市", "德阳市", "绵阳市", "广元市", "遂宁市", "内江市", "乐山市", "南充市", "眉山市", "宜宾市", "广安市", "达州市", "雅安市", "巴中市", "资阳市", "阿坝藏族羌族自治州", "甘孜藏族自治州", "凉山彝族自治州"],
            "贵州省": ["贵阳市", "六盘水市", "遵义市", "安顺市", "毕节市", "铜仁市", "黔西南布依族苗族自治州", "黔东南苗族侗族自治州", "黔南布依族苗族自治州"],
            "云南省": ["昆明市", "曲靖市", "玉溪市", "保山市", "昭通市", "丽江市", "普洱市", "临沧市", "楚雄彝族自治州", "红河哈尼族彝族自治州", "文山壮族苗族自治州", "西双版纳傣族自治州", "大理白族自治州", "德宏傣族景颇族自治州", "怒江傈僳族自治州", "迪庆藏族自治州"],
            "西藏自治区": ["拉萨市", "日喀则市", "昌都市", "林芝市", "山南市", "那曲市", "阿里地区"],
            "陕西省": ["西安市", "铜川市", "宝鸡市", "咸阳市", "渭南市", "延安市", "汉中市", "榆林市", "安康市", "商洛市"],
            "甘肃省": ["兰州市", "嘉峪关市", "金昌市", "白银市", "天水市", "武威市", "张掖市", "平凉市", "酒泉市", "庆阳市", "定西市", "陇南市", "临夏回族自治州", "甘南藏族自治州"],
            "青海省": ["西宁市", "海东市", "海北藏族自治州", "黄南藏族自治州", "海南藏族自治州", "果洛藏族自治州", "玉树藏族自治州", "海西蒙古族藏族自治州"],
            "宁夏回族自治区": ["银川市", "石嘴山市", "吴忠市", "固原市", "中卫市"],
            "新疆维吾尔自治区": ["乌鲁木齐市", "克拉玛依市", "吐鲁番市", "哈密市", "昌吉回族自治州", "博尔塔拉蒙古自治州", "巴音郭楞蒙古自治州", "阿克苏地区", "克孜勒苏柯尔克孜自治州", "喀什地区", "和田地区", "伊犁哈萨克自治州", "塔城地区", "阿勒泰地区"],
            "香港特别行政区": ["香港"],
            "澳门特别行政区": ["澳门"],
            "台湾省": ["台北市", "新北市", "桃园市", "台中市", "台南市", "高雄市"]
        }
        
        return province_cities.get(province, [province])
    
    def crawl_province(self, province, retry_count=3):
        """Crawl all data for a specific province"""
        logging.info(f"{'='*50}")
        logging.info(f"Starting province crawl: {province}")
        logging.info(f"{'='*50}")
        
        self.crawler.reset()
        cities = self.get_province_cities(province)
        
        for i, city in enumerate(cities):
            logging.info(f"Processing city {i+1}/{len(cities)}: {city}")
            try:
                self.crawler.crawl_city(city)
                time.sleep(2)
                logging.info(f"City {city} completed. Total records: {len(self.crawler.collected_data)}")
            except Exception as e:
                logging.error(f"Error crawling {city}: {e}")
                if retry_count > 0:
                    logging.info(f"Retrying {city}")
                    time.sleep(3)
                    return self.crawl_province(province, retry_count - 1)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        province_filename = province.replace(" ", "_").replace("自治区", "").replace("特别行政区", "")
        
        json_filename = os.path.join(self.output_dir, f"{province_filename}_pet_services_{timestamp}.json")
        csv_filename = os.path.join(self.output_dir, f"{province_filename}_pet_services_{timestamp}.csv")
        
        self.crawler.save_to_json(json_filename)
        self.crawler.save_to_csv(csv_filename)
        
        self.crawl_stats[province] = {
            "count": len(self.crawler.collected_data),
            "cities": len(cities),
            "json_file": json_filename,
            "csv_file": csv_filename,
            "status": "success"
        }
        
        logging.info(f"Province {province} completed. Total records: {len(self.crawler.collected_data)}")
        return True
    
    def crawl_all_provinces(self, exclude_provinces=None):
        """Crawl data for all provinces nationwide"""
        if exclude_provinces is None:
            exclude_provinces = []
        
        all_provinces = []
        for region, provinces in self.national_provinces.items():
            for province in provinces:
                if province not in exclude_provinces:
                    all_provinces.append((region, province))
        
        logging.info(f"Starting national crawl for {len(all_provinces)} provinces")
        if exclude_provinces:
            logging.info(f"Excluded provinces: {exclude_provinces}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_file = os.path.join(self.output_dir, f"crawl_statistics_{timestamp}.txt")
        
        for i, (region, province) in enumerate(all_provinces):
            logging.info(f"{'='*60}")
            logging.info(f"Progress: {i+1}/{len(all_provinces)} - Region: {region} - Province: {province}")
            logging.info(f"{'='*60}")
            
            try:
                self.crawl_province(province)
            except Exception as e:
                logging.error(f"Error crawling {province}: {e}")
                self.crawl_stats[province] = {
                    "count": 0,
                    "status": "failed",
                    "error": str(e)
                }
            
            time.sleep(3)
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("National Pet Service Business Data Collection Statistics\n")
            f.write(f"Collection Time: {timestamp}\n")
            f.write(f"Total Provinces: {len(all_provinces)}\n")
            f.write("="*60 + "\n\n")
            
            total_count = 0
            for region, provinces in self.national_provinces.items():
                f.write(f"\n【{region}】\n")
                for province in provinces:
                    if province in self.crawl_stats:
                        stats = self.crawl_stats[province]
                        status = stats.get("status", "unknown")
                        count = stats.get("count", 0)
                        total_count += count
                        f.write(f"  {province}: {count} records (Status: {status})\n")
            
            f.write(f"\n{'='*60}\n")
            f.write(f"Total: {total_count} records\n")
        
        logging.info(f"{'='*60}")
        logging.info("National data collection completed!")
        logging.info(f"Total records collected: {total_count}")
        logging.info(f"Statistics saved to: {stats_file}")
        logging.info(f"{'='*60}")
        
        return self.crawl_stats


def crawl_guangdong():
    """Standalone function to crawl Guangdong province only"""
    API_KEY = "YOUR_API_KEY_HERE"
    
    logging.info("="*60)
    logging.info("Starting Guangdong pet service data collection")
    logging.info("="*60)
    
    crawler = AmapPetServiceCrawler(API_KEY)
    guangdong_cities = [
        "广州市", "深圳市", "珠海市", "汕头市", "佛山市", "韶关市", "湛江市", "肇庆市",
        "江门市", "茂名市", "惠州市", "梅州市", "汕尾市", "河源市", "阳江市", "清远市",
        "东莞市", "中山市", "潮州市", "揭阳市", "云浮市"
    ]
    
    for city in guangdong_cities:
        crawler.crawl_city(city)
        time.sleep(1)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crawler.save_to_json(f"guangdong_pet_services_{timestamp}.json")
    crawler.save_to_csv(f"guangdong_pet_services_{timestamp}.csv")
    
    logging.info(f"Guangdong crawl completed. Total records: {len(crawler.collected_data)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('amap_crawler_complete.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Configuration
    API_KEY = "YOUR_API_KEY_HERE"
    MODE = "guangdong"  # "guangdong" or "national"
    OUTPUT_DIR = "pet_services_complete_data"
    EXCLUDE_PROVINCES = []
    
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        logging.error("Please set your Amap API Key in the code")
        exit(1)
    
    if MODE == "guangdong":
        crawl_guangdong()
    elif MODE == "national":
        manager = CrawlerManager(API_KEY, output_dir=OUTPUT_DIR)
        manager.crawl_all_provinces(exclude_provinces=EXCLUDE_PROVINCES)
    else:
        logging.error(f"Unknown mode: {MODE}")
        exit(1)