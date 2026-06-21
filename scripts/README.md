# Amap Pet Service Business Data Crawler

## Features

This program uses the Amap Maps Open Platform API to batch collect detailed information about pet service businesses in Guangdong Province and nationwide.

## Collected Information

### Required Information:
- Business Name
- Detailed Address
- Region (City/District)
- Contact Phone
- User Rating

### Additional Information:
- Business Coordinates (Latitude/Longitude)
- Service Type Tags
- Business Hours
- Average Cost

## Requirements

- Python 3.6+
- requests library

## Installation

```bash
pip install requests
```

## Usage

1. **Get Amap API Key**
   - Visit [Amap Open Platform](https://lbs.amap.com/) and register an account
   - Create an application and obtain an API Key

2. **Configure API Key**
   - Open `scripts/pet_service_crawler.py`
   - Replace `API_KEY = "YOUR_API_KEY_HERE"` with your actual API Key

3. **Run the Program**
   ```bash
   python scripts/pet_service_crawler.py
   ```

4. **View Results**
   - After running, the program will generate files:
     - `guangdong_pet_services_timestamp.json` - JSON format data
     - `guangdong_pet_services_timestamp.csv` - CSV format data
     - `amap_crawler_complete.log` - Log file

## Program Features

1. **Nationwide Coverage**: Supports collecting data from all 34 provincial-level regions in China
2. **Multi-keyword Search**: Uses multiple pet-related keywords for comprehensive data collection
3. **Pagination Support**: Automatically handles pagination for complete data retrieval
4. **API Rate Limiting**: Intelligent API call frequency control to prevent restrictions
5. **Data Deduplication**: Removes duplicate entries based on business ID
6. **Error Handling**: Comprehensive error handling mechanisms
7. **Logging**: Detailed logging for troubleshooting
8. **Multiple Formats**: Supports both JSON and CSV output formats

## Configuration Options

- **MODE**: Set to "guangdong" for Guangdong-only crawl or "national" for nationwide crawl
- **OUTPUT_DIR**: Custom output directory path
- **EXCLUDE_PROVINCES**: List of provinces to exclude (national mode only)

## Notes

1. **API Key Limits**: Amap API has call limits, please use responsibly
2. **Runtime**: The program may take a long time due to large data collection
3. **Network Stability**: Ensure stable network connection
4. **Data Completeness**: Some businesses may have missing fields which are handled as empty values

## Code Structure

- `AmapPetServiceCrawler` class: Core crawler class
  - `__init__`: Initialize configuration
  - `search_pet_services`: Call API to search pet services
  - `process_business_data`: Process business data
  - `crawl_city`: Crawl data for a single city
  - `save_to_json`: Save data as JSON
  - `save_to_csv`: Save data as CSV

- `CrawlerManager` class: Manages nationwide crawl tasks
  - `crawl_province`: Crawl data for a specific province
  - `crawl_all_provinces`: Crawl data for all provinces

- Main entry: Configure API Key and start crawler
