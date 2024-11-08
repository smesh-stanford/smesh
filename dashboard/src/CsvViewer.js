import React, { useState, useEffect } from 'react';
import Papa from 'papaparse'; // Library to parse CSV

// Use React component libraries, no need to make own table.

const CsvViewer = () => {
  const [csvData, setCsvData] = useState([]);

  // Function to fetch CSV file path from Flask and load the CSV
  const loadCSV = async () => {
    try {
      // Fetch data CSV file URL from Flask backend
      const response = await fetch('http://localhost:5000/get-data');
      const data = await response.text();

      // Parse CSV content using PapaParse
      Papa.parse(data, {
        header: true, // Set to true if you have headers
        complete: (result) => {
          setCsvData(result.data); // Set parsed data into state
        }
      });
    } catch (error) {
      console.error('Error fetching or parsing CSV:', error);
    }
  };

  // Call loadCSV() when the component mounts
  useEffect(() => {
    loadCSV();
  }, []);

  // Render CSV data in a table
  return (
    <div>
      <h1>Smoke Sensor Data</h1>
      <div className="table-container">
        {csvData.length > 0 ? (
            <table>
            <thead>
                <tr>
                {/* Dynamically render table headers based on CSV keys */}
                {Object.keys(csvData[0]).map((key) => (
                    <th key={key}>{key}</th>
                ))}
                </tr>
            </thead>
            <tbody>
                {csvData.map((row, index) => (
                <tr key={index}>
                    {Object.values(row).map((value, i) => (
                    <td key={i}>{value}</td>
                    ))}
                </tr>
                ))}
            </tbody>
            </table>
        ) : (
            <p>Loading CSV data...</p>
        )}
      </div>
    </div>
  );
};

export default CsvViewer;