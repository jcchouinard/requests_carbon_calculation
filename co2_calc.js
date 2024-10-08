import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { co2 } from "@tgwf/co2";

// Define __dirname in ES module scope
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

(async () => {
  try {
    // Read the data from the page_data.json file
    const dataFilePath = path.join(__dirname, 'page_data.json');
    if (!fs.existsSync(dataFilePath)) {
      throw new Error('No data file found. Please run the Python script first.');
    }

    const data = JSON.parse(fs.readFileSync(dataFilePath, 'utf8'));

    const options = {
      verbose: false,
      userAgentIdentifier: "myGreenApp",
    };

    for (const [url, metrics] of Object.entries(data)) {
      for (const [key, values] of Object.entries(metrics)) {
        const { page_size } = values;

        // Check green hosting
        const greenHost = true; // Placeholder for actual green hosting check

        // Calculate emissions
        const emissions = new co2().perByte(page_size, greenHost);
        
        // Fill in the emissions data in mg (1 kg = 1000 mg)
        values.co2_emissions = emissions * 1000; // Convert kg to mg

        console.log(`URL: ${url}, Mode: ${key}`);
        console.log(`Page weight: ${(page_size / 1000).toFixed(2)} KB`);
        console.log(`Emissions: ${(values.co2_emissions).toFixed(3)} mg of CO2`);
      }
    }

    // Save updated data to JSON file
    fs.writeFileSync(dataFilePath, JSON.stringify(data, null, 2));

  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
})();
