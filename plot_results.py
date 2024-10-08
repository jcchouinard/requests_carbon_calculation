import json
import matplotlib.pyplot as plt
import numpy as np

# Load the data
with open('page_data.json', 'r') as file:
    data = json.load(file)

len(data.keys())

filtered_dict = {}
for k,v in data.items():
    if all(not isinstance(sv, str) for sv in v.values()):
        filtered_dict[k] = v

data = filtered_dict

def plot_simple_comparisons():
    comparisons = [
        ('non_headless_light', 'non_headless_dark'),
        ('headless_light', 'headless_dark'),
        ('head_requests', 'get_requests'),
    ]
    # Prepare to collect data for each comparison
    for comparison in comparisons:
        mode1, mode2 = comparison
        emissions1 = []
        emissions2 = []

        # Extract emissions data from the JSON
        for url, metrics in data.items():
            if mode1 in metrics and mode2 in metrics:
                emissions1.append(metrics[mode1].get('co2_emissions', 0))
                emissions2.append(metrics[mode2].get('co2_emissions', 0))

        # Filter out None/Null and zero values, then sort emissions
        emissions1 = sorted(filter(lambda x: x is not None and x > 0, emissions1))
        emissions2 = sorted(filter(lambda x: x is not None and x > 0, emissions2))

        # Ensure both emissions lists are of the same length
        min_length = min(len(emissions1), len(emissions2))
        emissions1 = emissions1[:min_length]
        emissions2 = emissions2[:min_length]

        # Calculate percentiles at every 5th percent (0, 5, 10, ..., 100)
        percentiles = np.arange(0, 101, 5)
        p_values1 = np.percentile(emissions1, percentiles)
        p_values2 = np.percentile(emissions2, percentiles)

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(percentiles, p_values1, marker='o', label=f'{mode1} Percentiles', color='blue')
        plt.plot(percentiles, p_values2, marker='o', label=f'{mode2} Percentiles', color='orange')

        plt.xlabel('Percentile')
        plt.ylabel('CO2 Emissions (mg)')
        plt.title(f'CO2 Emissions Percentiles: {mode1} vs {mode2}')
        plt.legend()
        plt.grid(True)
        plt.xticks(np.arange(0, 110, 10))  # Set x-ticks for percentiles
        plt.xlim([0, 100])
        plt.ylim(bottom=0)  # Start y-axis from 0 for better visibility
        plt.show()

def plot_headless_vs_non():
    comparisons = [
        ('non_headless', 'headless')
    ]
    # Prepare to collect data for each comparison
    for comparison in comparisons:
        mode1, mode2 = comparison
        emissions1 = []  # Non-headless emissions
        emissions2 = []  # Headless emissions

        # Extract emissions data from the JSON
        for url, metrics in data.items():
            if mode1 == 'non_headless':
                # Combine emissions from both non-headless modes
                non_headless_light = metrics.get('non_headless_light', {}).get('co2_emissions', None)
                non_headless_dark = metrics.get('non_headless_dark', {}).get('co2_emissions', None)

                # Check if values are valid numbers
                if isinstance(non_headless_light, (int, float)) and non_headless_light > 0:
                    emissions1.append(non_headless_light)
                if isinstance(non_headless_dark, (int, float)) and non_headless_dark > 0:
                    emissions1.append(non_headless_dark)

            if mode2 == 'headless':
                # Combine emissions from both headless modes
                headless_light = metrics.get('headless_light', {}).get('co2_emissions', None)
                headless_dark = metrics.get('headless_dark', {}).get('co2_emissions', None)

                # Check if values are valid numbers
                if isinstance(headless_light, (int, float)) and headless_light > 0:
                    emissions2.append(headless_light)
                if isinstance(headless_dark, (int, float)) and headless_dark > 0:
                    emissions2.append(headless_dark)

        # Filter out None/Null values and sort emissions
        emissions1 = sorted(emissions1)
        emissions2 = sorted(emissions2)

        # # Print the emissions for debugging
        # print(f"Emissions for {mode1}: {emissions1}")
        # print(f"Emissions for {mode2}: {emissions2}")

        # # Check if the lists are empty before calculating percentiles
        # if not emissions1 or not emissions2:
        #     print(f"Skipping comparison for {mode1} and {mode2} due to empty emissions lists.")
        #     continue

        # Calculate percentiles at every 5th percent (0, 5, 10, ..., 100)
        percentiles = np.arange(0, 101, 5)
        p_values1 = np.percentile(emissions1, percentiles)
        p_values2 = np.percentile(emissions2, percentiles)

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(percentiles, p_values1, marker='o', label=f'{mode1} (Combined) Percentiles', color='blue')
        plt.plot(percentiles, p_values2, marker='o', label=f'{mode2} (Combined) Percentiles', color='orange')

        plt.xlabel('Percentile')
        plt.ylabel('CO2 Emissions (mg)')
        plt.title(f'CO2 Emissions Percentiles: {mode1} (Combined) vs {mode2} (Combined)')
        plt.legend()
        plt.grid(True)
        plt.xticks(np.arange(0, 110, 10))  # Set x-ticks for percentiles
        plt.xlim([0, 100])
        plt.ylim(bottom=0)  # Start y-axis from 0 for better visibility
        plt.show()



def plot_get_vs_headless():
    comparisons = [
        ('headless', 'get_requests')
    ]

    # Prepare to collect data for each comparison
    for comparison in comparisons:
        mode1, mode2 = comparison
        emissions1 = []  # Headless emissions
        emissions2 = []  # Get requests emissions

        # Extract emissions data from the JSON
        for url, metrics in data.items():
            if mode1 == 'headless':
                # Combine emissions from both headless modes
                headless_light = metrics.get('headless_light', {}).get('co2_emissions', None)
                headless_dark = metrics.get('headless_dark', {}).get('co2_emissions', None)

                # Check if values are valid numbers
                if isinstance(headless_light, (int, float)) and headless_light > 0:
                    emissions1.append(headless_light)
                if isinstance(headless_dark, (int, float)) and headless_dark > 0:
                    emissions1.append(headless_dark)

            if mode2 == 'get_requests':
                # Get emissions from get_requests mode
                get_requests = metrics.get('get_requests', {}).get('co2_emissions', None)

                # Check if value is a valid number
                if isinstance(get_requests, (int, float)) and get_requests > 0:
                    emissions2.append(get_requests)

        # Filter out None/Null values and sort emissions
        emissions1 = sorted(emissions1)
        emissions2 = sorted(emissions2)
        
        # Calculate percentiles at every 5th percent (0, 5, 10, ..., 100)
        percentiles = np.arange(0, 101, 5)
        p_values1 = np.percentile(emissions1, percentiles)
        p_values2 = np.percentile(emissions2, percentiles)

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(percentiles, p_values1, marker='o', label=f'{mode1} (Combined) Percentiles', color='blue')
        plt.plot(percentiles, p_values2, marker='o', label=f'{mode2} Percentiles', color='orange')

        plt.xlabel('Percentile')
        plt.ylabel('CO2 Emissions (mg)')
        plt.title(f'CO2 Emissions Percentiles: {mode1} (Combined) vs {mode2}')
        plt.legend()
        plt.grid(True)
        plt.xticks(np.arange(0, 110, 10))  # Set x-ticks for percentiles
        plt.xlim([0, 100])
        plt.ylim(bottom=0)  # Start y-axis from 0 for better visibility
        plt.show()


plot_simple_comparisons()
plot_headless_vs_non()
plot_get_vs_headless()