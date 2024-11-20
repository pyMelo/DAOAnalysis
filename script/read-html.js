const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Function to create a directory if it doesn't exist
const createDirectory = (dirName) => {
    if (!fs.existsSync(dirName)) {
        fs.mkdirSync(dirName, { recursive: true });
        console.log(`Directory "${dirName}" created.`);
    } else {
        console.log(`Directory "${dirName}" already exists.`);
    }
};

// Function to convert JSON data to CSV
const jsonToCsv = (data, filePath) => {
    const csvRows = [];
    const headers = data.headers.join(','); // Convert headers array to CSV format
    csvRows.push(headers);

    // Add rows
    data.rows.forEach(row => {
        csvRows.push(row.join(',')); // Convert each row array to CSV format
    });

    // Write CSV to file
    const csvContent = csvRows.join('\n');
    fs.writeFileSync(filePath, csvContent, 'utf-8');
    console.log(`CSV file generated: ${filePath}`);
};

// Function to save a canvas element as a PNG
const saveCanvasAsPng = async (page, canvasId, filePath) => {
    const canvasDataUrl = await page.evaluate((canvasId) => {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return null; // Return null if canvas is not found
        }
        return canvas.toDataURL(); // Get the canvas data as a Base64-encoded URL
    }, canvasId);

    if (!canvasDataUrl) {
        console.error(`Canvas with ID "${canvasId}" not found.`);
        return;
    }

    // Decode Base64 data and save as a PNG file
    const base64Data = canvasDataUrl.replace(/^data:image\/png;base64,/, '');
    fs.writeFileSync(filePath, base64Data, 'base64');
    console.log(`Canvas "${canvasId}" saved as ${filePath}`);
};

// Function to extract a single table in a range and clean it
const extractAndCleanTable = async (page, startId, endId) => {
    const tableData = await page.evaluate((startId, endId) => {
        const startElement = document.getElementById(startId);
        const endElement = document.getElementById(endId);

        if (!startElement || !endElement) {
            return { error: 'Start or end element not found in the DOM.' };
        }

        const rangeElements = [];
        let currentElement = startElement.nextElementSibling;
        while (currentElement && currentElement !== endElement) {
            rangeElements.push(currentElement);
            currentElement = currentElement.nextElementSibling;
        }

        const table = rangeElements.find(el => el.tagName && el.tagName.toLowerCase() === 'table');
        if (!table) {
            return { error: 'No table found within the specified range.' };
        }

        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr =>
            Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
        );

        return { headers, rows };
    }, startId, endId);

    if (tableData.error) {
        return tableData; // Return the error as-is
    }

    // Remove "Type" and "Capabilities" columns
    const typeIndex = tableData.headers.indexOf('Type');
    const capabilitiesIndex = tableData.headers.indexOf('Capabilities');

    const filteredHeaders = tableData.headers.filter((_, i) => i !== typeIndex && i !== capabilitiesIndex);
    const filteredRows = tableData.rows
        .filter((_, i) => i !== tableData.rows.length - 1) // Remove the last row (total)
        .map(row => row.filter((_, i) => i !== typeIndex && i !== capabilitiesIndex));

    return { headers: filteredHeaders, rows: filteredRows };
};

(async () => {
    // Input variables from command line
    const filePrefix = process.argv[2]; // First argument: File prefix
    const outputDir = process.argv[2];  // Second argument: Output directory
    const htmlFileName = process.argv[2]; // Third argument: HTML file name (without extension)

    if (!filePrefix || !outputDir || !htmlFileName) {
        console.error('Usage: node script.js <DAO>');
        process.exit(1);
    }

    // Create the output directory
    createDirectory(outputDir);

    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    const filePath = path.resolve(__dirname, `../SolidityMetricsHTML/${htmlFileName}.html`);
    await page.goto(`file://${filePath}`, { waitUntil: 'networkidle0' });

    // Extract and save the first table (cleaned)
    const range1StartId = 'spanidtsourceunitsinscopesourceunitsinscopespan';
    const range1EndId = 't-deployable-contracts';
    const table1Data = await extractAndCleanTable(page, range1StartId, range1EndId);

    if (table1Data.error) {
        console.error(table1Data.error);
    } else {
        const table1FilePath = path.join(outputDir, `${filePrefix}solidity-files.csv`);
        jsonToCsv(table1Data, table1FilePath);
    }

    // Extract all tables in Range 2 and merge them
    const range2StartId = 'spanidtexposedfunctionsexposedfunctionsspan';
    const range2EndId = 'spanidtstatevariablesstatevariablesspan';

    const tablesInRange2 = await page.evaluate((startId, endId) => {
        const startElement = document.getElementById(startId);
        const endElement = document.getElementById(endId);

        if (!startElement || !endElement) {
            return { error: 'Start or end element not found in the DOM.' };
        }

        const rangeElements = [];
        let currentElement = startElement.nextElementSibling;
        while (currentElement && currentElement !== endElement) {
            rangeElements.push(currentElement);
            currentElement = currentElement.nextElementSibling;
        }

        const tables = rangeElements.filter(el => el.tagName && el.tagName.toLowerCase() === 'table');
        if (tables.length === 0) {
            return { error: 'No tables found within the specified range.' };
        }

        return tables.map(table => {
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr =>
                Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
            );
            return { headers, rows };
        });
    }, range2StartId, range2EndId);

    if (tablesInRange2.error) {
        console.error(tablesInRange2.error);
    } else {
        // Combine headers and rows into a single table structure
        let mergedHeaders = [];
        let mergedRow = [];

        tablesInRange2.forEach(tableData => {
            mergedHeaders = mergedHeaders.concat(tableData.headers);
            tableData.rows.forEach(row => {
                mergedRow = mergedRow.concat(row);
            });
        });

        const csvFilePath = path.join(outputDir, `${filePrefix}functions.csv`);
        jsonToCsv({ headers: mergedHeaders, rows: [mergedRow] }, csvFilePath);
    }

    // Save the specified canvas elements as PNG images
    await saveCanvasAsPng(page, 'chart-risk-summary', path.join(outputDir, `${filePrefix}risk-summary.png`));
    await saveCanvasAsPng(page, 'chart-nsloc-total', path.join(outputDir, `${filePrefix}nsloc-total.png`));

    await browser.close();
})();
