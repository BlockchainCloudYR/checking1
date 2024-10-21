const fs = require('fs');
const path = require('path');
const { Keypair } = require('@solana/web3.js');
const bs58 = require('bs58');

// Generate a new keypair
const keypair = Keypair.generate();

// Extract the public and private keys
const publicKey = keypair.publicKey.toString();
const secretKey = bs58.encode(keypair.secretKey);  // Convert secretKey to Base58

// Define the directory and file path for Solana keypair.json
const solanaDir = path.join('C:', 'Users', 'rajsh', 'AppData', 'Local', 'Solana');

// Ensure the directory exists
if (!fs.existsSync(solanaDir)) {
    fs.mkdirSync(solanaDir, { recursive: true });
}

const filePath = path.join(solanaDir, 'keypair.json');

// Read the existing file content, if it exists
let existingData = [];
if (fs.existsSync(filePath)) {
    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');

        // Check if the file has valid content, otherwise initialize as an empty array
        if (fileContent) {
            existingData = JSON.parse(fileContent);

            // If the parsed content is not an array, initialize it as an empty array
            if (!Array.isArray(existingData)) {
                existingData = [];
            }
        }
    } catch (err) {
        console.error('Error parsing JSON file:', err);
        existingData = [];  // Initialize as an empty array in case of error
    }
}

// Function to convert UTC time to IST
function getISTTime() {
    const currentTime = new Date();
    const utcTime = currentTime.getTime() + (currentTime.getTimezoneOffset() * 60000);
    const istOffset = 5.5 * 60 * 60 * 1000;  // IST is UTC + 5:30
    const istTime = new Date(utcTime + istOffset);

    // Manually format the IST time in ISO format without using toISOString()
    const year = istTime.getFullYear();
    const month = String(istTime.getMonth() + 1).padStart(2, '0');
    const day = String(istTime.getDate()).padStart(2, '0');
    const hours = String(istTime.getHours()).padStart(2, '0');
    const minutes = String(istTime.getMinutes()).padStart(2, '0');
    const seconds = String(istTime.getSeconds()).padStart(2, '0');
    const milliseconds = String(istTime.getMilliseconds()).padStart(3, '0');

    // Return the formatted IST timestamp
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}+05:30`;
}

// Append the new keypair to the existing data
existingData.push({
    publicKey,
    secretKey,
    timestamp: getISTTime()  // Add a timestamp for reference
});

// Save the updated data back to the file in the specified directory
fs.writeFileSync(filePath, JSON.stringify(existingData, null, 2));  // Formatting for readability

// Output the keys in human-readable form
console.log("Public Key:", publicKey);
console.log("Secret Key (Base58):", secretKey);
