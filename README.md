# Estimate Carbon Emissions of Different Types of Requests

My goal was to estimate the carbon emissions of scraping websites in different scenarions:

- Head VS Get Requests
- Get Requests VS Rendered Selenium Browser Automation
- Dark mode vs light mode content.
- Headless vs non-headless Browser Automation

The estimation is made on the number of bytes transferred.

Thus, the Headless vs non-headless Browser Automation is not representative of the real world.

I tried to evaluate CPU usage in those cases.

This is using Selenium and [co2.js](https://developers.thegreenwebfoundation.org/co2js/overview/) from the greenwebfoundation.

## Getting Started

[install node and npm](https://www.jcchouinard.com/install-node-and-npm/)

## Install co2.js
`npm install @tgwf/co2`

## Run scrape_domains.py 

## Run co2_calc.js


## Results

To understand the results you have to consider what was measured. In my case, only the amount of bytes transferred.


My experiment looks at bytes transferred, not energy used by the monitor to render the page on the device. This means that:

- It should not be impacted by dark mode
- It should not impact bots running in headless mode


That being said, the above should be true, unless developers intentionally delivered different data in headless or dark mode. For instance Reddit does not allow crawling in headless, thus bytes transferred were a lot smaller.

### Non-headless VS Headless

The same number of bytes was transferred in headless and non-healess. 

However, to really know the carbon impact of headless, I would have needed to plug an energy monitor on the device to see how much energy was consumed by both devices.


### Dark mode vs Light Mode

The same number of bytes was transferred in dark and Light modes. 

However, to really know the carbon impact of headless, I would have needed to plug an energy monitor on a LCD monitor and a OLED monitor to see how much energy was consumed by both devices.

### Non-Headless_light vs non_headless_dark

In this case,the same amount of bytes should be trasferred in dark or light modes, and we will see if that is true. Dark mode has an impact on the electricity required to render the page on the user screen, not the number of bytes transformed.

## Other useful resources:
- [co2.js on Github](https://github.com/thegreenwebfoundation/co2.js)
- [Useful wrapper for co2.js: Tracking carbon emissions in end-to-end tests](https://www.the-public-good.com/web-development/sustainable-reporting-emissions)
- [Does Dark Mode Saves Battery](https://bejamas.io/blog/does-dark-mode-save-battery)


## Next Steps

Use Mac Energy Usage in Activity Monitor to track energy consumption. https://www.rdegges.com/2022/how-to-calculate-the-energy-consumption-of-a-mac/


Wattage=Voltage (V)×Current (A)
https://stackoverflow.com/questions/4602828/how-to-get-power-usage-on-a-mac 