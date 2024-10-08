import json
import os
import requests
import pandas as pd
import psutil
from selenium import webdriver
from tldextract import extract


# Function to fetch URL size and take a screenshot using Selenium
def fetch_url(url, name, options):
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)
        driver.get(url)
        page_source = driver.page_source
        size_in_bytes = len(page_source.encode('utf-8'))
        if url in top_15:
            out_path = url.replace('https://www.', '').replace('.', '_').replace('https://', '')
            if not os.path.isdir(f'screenshots/{out_path}'):
                os.mkdir(f'screenshots/{out_path}')
            driver.get_screenshot_as_file(f'screenshots/{out_path}/{name}.png')
        driver.quit()

        return size_in_bytes
    except Exception as e:
        print('Selenium had an error:', e)


# Function to calculate page size and energy consumption for GET and HEAD requests
def analyze_requests(url):
    results = {}

    # HEAD Request
    try:
        head_response = requests.head(url, timeout=10)
        head_size_kb = int(head_response.headers.get('Content-Length', 0)) / 1024  # Convert to KB
        head_energy_used = 0
        head_page_size = head_size_kb * 1024
    except Exception as e:
        head_size_kb = f'head request error: {e}'
        head_page_size =  f'head request error: {e}'
    # GET Request
    try:
        get_response = requests.get(url, timeout=10)
        get_size_kb = len(get_response.content) / 1024  # Convert to KB
        get_energy_used = 0
        get_page_size = get_size_kb * 1024
    except Exception as e:
        head_size_kb = f'body request error: {e}'
        get_page_size = f'body request error: {e}'

    results['head_requests'] = {
        'size_kb': head_size_kb,
        'page_size': head_page_size,
        'co2_emissions': head_energy_used,
    }
    results['get_requests'] = {
        'size_kb': get_size_kb,
        'page_size': get_page_size,
        'co2_emissions': get_energy_used,
    }

    return results

def get_domain(url):
    u = 'https://' + url
    return extract(u).domain

# Load URLs from CSV
df = pd.read_csv(
    'https://www.domcop.com/files/top/top10milliondomains.csv.zip',
    compression='zip'
)

subset = df[:10000]

subset['netloc'] = subset['Domain'].apply(get_domain)
subset = subset.drop_duplicates(subset='netloc')
urls = 'https://' + subset['Domain'][:3]  # Just using first 3 domains for testing
top_15 = list('https://' + subset['Domain'][:15] )
top_15 += ['https://' + domain for domain in subset['Domain'].sample(n=5, random_state=1).tolist()]

# Data structure to hold results
data = {}

done = list(data.keys())

for url in urls:
    if url in done:
        continue   
    else:
        print('Running: ', url)
        data[url] = {
            "non_headless_light": {'page_size': 0, 'total_cpu_time': 0, 'co2_emissions': 0},
            "non_headless_dark": {'page_size': 0, 'total_cpu_time': 0, 'co2_emissions': 0},
            "headless_light": {'page_size': 0, 'total_cpu_time': 0, 'co2_emissions': 0},
            "headless_dark": {'page_size': 0, 'total_cpu_time': 0, 'co2_emissions': 0},
        }
        
        # Include GET and HEAD request results at the same level
        data[url].update(analyze_requests(url))  # Update the dictionary with request results

        for i in ["--enable-features=WebContentsForceDark", "--disable-features=WebContentsForceDark"]:
            is_dark = 'dark' if 'enable' in i else 'light'

            for b in [True, False]:
                options = webdriver.ChromeOptions()
                out = 'headless' if b else 'non_headless'
                if b:
                    options.add_argument('--headless=new')

                name = f'{out}_{is_dark}'
                options.add_argument(i)

                # Measure CPU usage before fetching the URL
                initial_cpu = psutil.cpu_percent(interval=2)

                try:
                    # Fetch URL size using Selenium
                    data[url][name]['page_size'] = fetch_url(url, name, options)

                    # Measure CPU usage after fetching the URL
                    final_cpu = psutil.cpu_percent(interval=2)

                    # Calculate CPU time consumed
                    total_cpu_time = final_cpu - initial_cpu
                    data[url][name]['total_cpu_time'] = total_cpu_time

                except Exception as e:
                    print(f"Error fetching {url} in {name}: {e}")
                    data[url][name]['page_size'] = f'error: {e}'
                    data[url][name]['total_cpu_time'] = f'error: {e}'
    done.append(url)
# Save the data to a JSON file
with open('page_data.json', 'w') as f:
    json.dump(data, f, indent=2)



