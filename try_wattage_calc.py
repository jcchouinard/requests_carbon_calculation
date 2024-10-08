import json
import os
import requests
from selenium import webdriver
from tldextract import extract
import subprocess
import re
import time

# Function to fetch battery wattage
def get_battery_wattage():
    try:
        # Run the ioreg command to get battery data
        command = "ioreg -n AppleSmartBatteryManager -r -l | grep -iE '(Amp|Watt|Volt)'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if any output was returned
        if result.stdout:
            # Extract relevant values using regular expressions
            voltage_match = re.search(r'"Voltage" = (\d+)', result.stdout)
            amperage_match = re.search(r'"Amperage" = (\d+)', result.stdout)

            if voltage_match and amperage_match:
                # Get the values in millivolts and milliamps
                voltage_mV = int(voltage_match.group(1))
                amperage_mA = int(amperage_match.group(1))

                # Convert to volts and amps
                voltage_V = voltage_mV / 1000  # Convert from mV to V
                amperage_A = amperage_mA / 1000  # Convert from mA to A

                # Calculate wattage
                wattage = voltage_V * amperage_A

                return {
                    "Voltage (V)": voltage_V,
                    "Amperage (A)": amperage_A,
                    "Wattage (W)": wattage
                }
            else:
                return "Voltage or Amperage not found in the output."
        else:
            return "No output returned from the command."
    except Exception as e:
        return f"Error fetching battery data: {e}"

# Function to fetch URL size and take a screenshot using Selenium
def fetch_url(url, name, options):
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)
        driver.get(url)
        page_source = driver.page_source
        size_in_bytes = len(page_source.encode('utf-8'))
        
        # Check if the URL is in top_15 for screenshots
        if url in top_15:
            out_path = url.replace('https://www.', '').replace('.', '_').replace('https://', '')
            if not os.path.isdir(f'screenshots/{out_path}'):
                os.mkdir(f'screenshots/{out_path}')
            driver.get_screenshot_as_file(f'screenshots/{out_path}/{name}.png')
        
        driver.quit()
        return size_in_bytes
    except Exception as e:
        print('Selenium had an error:', e)
        return 0

# Function to calculate page size and energy consumption for GET and HEAD requests
def analyze_requests(url):
    results = {}

    # HEAD Request
    try:
        head_response = requests.head(url, timeout=10)
        head_size_kb = int(head_response.headers.get('Content-Length', 0)) / 1024  # Convert to KB
        head_page_size = head_size_kb * 1024
    except Exception as e:
        head_size_kb = f'head request error: {e}'
        head_page_size = f'head request error: {e}'

    # GET Request
    try:
        get_response = requests.get(url, timeout=10)
        get_size_kb = len(get_response.content) / 1024  # Convert to KB
        get_page_size = get_size_kb * 1024
    except Exception as e:
        get_size_kb = f'body request error: {e}'
        get_page_size = f'body request error: {e}'

    results['head_requests'] = {
        'size_kb': head_size_kb,
        'page_size': head_page_size,
        'wattage': 0,  # Initialize as 0, will update later
    }
    results['get_requests'] = {
        'size_kb': get_size_kb,
        'page_size': get_page_size,
        'wattage': 0,  # Initialize as 0, will update later
    }

    return results

def get_domain(url):
    u = 'https://' + url
    return extract(u).domain

# Assuming you have a subset of data loaded into `subset`
subset = subset.drop_duplicates(subset='netloc')
urls = ['https://' + domain for domain in subset['Domain'][20:31]]  # Adjusted to 100 for testing
top_15 = list('https://' + subset['Domain'][:15])
top_15 += ['https://' + domain for domain in subset['Domain'].sample(n=5, random_state=1).tolist()]
top_15.append('https://reddit.com')

# Data structure to hold results
data = {}
done = {}

# Define options for different modes
modes = [
    {"dark": True, "headless": False},
    {"dark": True, "headless": True},
    {"dark": False, "headless": False},
    {"dark": False, "headless": True},
]

# Batch process 10 websites at a time for each mode
for mode in modes:
    is_dark = mode["dark"]
    is_headless = mode["headless"]

    # Set the options for the browser
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument('--headless=new')
    options.add_argument('--disable-cache')
    options.add_argument('--enable-features=WebContentsForceDark' if is_dark else '--disable-features=WebContentsForceDark')

    # Initialize cumulative wattage
    cumulative_wattage = 0
    count = 0
    mode_key = f"{'dark' if is_dark else 'light'}_{'headless' if is_headless else 'non-headless'}"

    # Initialize mode-specific data structure
    done[mode_key] = {"cumulative_wattage": 0, "urls": {}}

    for url in urls:
        print('Running: ', url)

        # Analyze requests before fetching URLs
        data[url] = {"page_size": 0, "wattage": 0}
        data[url].update(analyze_requests(url))

        # Measure battery wattage before fetching the URLs
        initial_battery_data = get_battery_wattage()
        initial_wattage = initial_battery_data.get("Wattage (W)", 0)

        # Fetch URL size using Selenium
        data[url]['page_size'] = fetch_url(url, "screenshot", options)

        # Measure battery wattage after fetching the URLs
        final_battery_data = get_battery_wattage()
        final_wattage = final_battery_data.get("Wattage (W)", 0)

        # Calculate wattage used during this iteration
        wattage_used = initial_wattage - final_wattage
        data[url]['wattage'] = wattage_used
        cumulative_wattage += wattage_used
        count += 1

        # Store the data for this URL in the mode-specific data structure
        done[mode_key]["urls"][url] = data[url]

        # After every 10 websites, log the cumulative wattage and reset the counter
        if count == 10:
            done[mode_key]["cumulative_wattage"] += cumulative_wattage
            print(f"Cumulative wattage for 10 websites in {mode_key}: {cumulative_wattage:.2f} W")
            cumulative_wattage = 0
            count = 0

    # Add any remaining wattage that wasn't logged after the last batch of websites
    if count > 0:
        done[mode_key]["cumulative_wattage"] += cumulative_wattage

# Save the data to a JSON file
with open('page_data.json', 'w') as f:
    json.dump(done, f, indent=2)