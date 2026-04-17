const { MongoClient } = require("mongodb");
const path = require("path");
const fs = require("fs");

// Load .env file manually
function loadEnv() {
  const envPath = path.resolve(__dirname, "..", ".env");

  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, "utf8");

    envContent.split(/\r?\n/).forEach((line) => {
      const match = line.match(/^\s*([^#\s][^=]*)\s*=\s*(.*)$/);

      if (match) {
        const key = match[1].trim();
        const value = match[2].trim().replace(/^["'](.*)["']$/, "$1");

        if (!process.env[key]) {
          process.env[key] = value;
        }
      }
    });
  }
}

// Load environment variables
loadEnv();

// MongoDB connection URI
const uri = process.env.MONGODB_URI;

// Mongo client
const client = new MongoClient(uri);

// Connect function
async function connectToDatabase() {
  try {
    await client.connect();
    console.log("✅ Connected to MongoDB Atlas");

    const dbName = process.env.MONGODB_DB_NAME || "price_comparison";
    const db = client.db(dbName);

    return db;
  } catch (error) {
    console.error("❌ Failed to connect to database:", error);
    process.exit(1);
  }
}

module.exports = { connectToDatabase, client };