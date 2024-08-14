const functions = require("firebase-functions");
const { execSync } = require("child_process");
const cors = require("cors")({ origin: true });
const { spawn } = require("child_process");
const path = require("path");

// Install the Python dependencies before running the function
execSync("pip install -r requirements.txt");

exports.stockData = functions
  .region('europe-west6')
  .https.onRequest((req, res) => {
    cors(req, res, () => {
      const symbol = req.query.symbol;
      if (!symbol) {
        console.error("No stock symbol provided.");
        return res.status(400).json({ error: "No stock symbol provided." });
      }

      const pythonProcess = spawn("python3", [path.join(__dirname, "main.py"), symbol]);

      pythonProcess.stdout.on("data", (data) => {
        console.log("Python script output:", data.toString());
        try {
          const result = JSON.parse(data.toString());
          res.json(result);
        } catch (err) {
          console.error("Error parsing JSON from Python script:", err);
          res.status(500).json({ error: "Failed to parse data.", details: err.toString() });
        }
      });

      pythonProcess.stderr.on("data", (data) => {
        console.error("Error from Python script:", data.toString());
        res.status(500).json({ error: "Error from Python script.", details: data.toString() });
      });

      pythonProcess.on("close", (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}`);
          res.status(500).json({ error: `Python script exited with code ${code}` });
        }
      });
    });
  });

