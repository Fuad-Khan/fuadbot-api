import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import fetch from "node-fetch";
import fs from "fs";

dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Debug logger (only in dev)
const debugLog = (...args) => {
  if (process.env.NODE_ENV !== "production") {
    console.log(...args);
  }
};

// Load system prompt
const systemPrompt = fs.readFileSync("./prompt/systemPrompt.txt", "utf-8");

// Chat endpoint
app.post("/chat", async (req, res) => {
  const { message } = req.body;

  if (!message || typeof message !== "string") {
    return res.status(400).json({ error: "Invalid message input." });
  }

  const cleanMsg = message.trim().toLowerCase();
  debugLog("🛎️ Received message:", message);

  // Special case handler
  if (/tell about me/i.test(cleanMsg)) {
    return res.json({
      reply:
        "Do you want me to tell you about Fuad Khan or about yourself? I can only provide info about Fuad Khan.",
    });
  }

  const today = new Date().toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000); // 10s timeout

  try {
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama3-8b-8192",
        messages: [
          {
            role: "system",
            content: `${systemPrompt}\n\n📅 Today's Date: ${today}`,
          },
          {
            role: "user",
            content: `${message} (Answer briefly and only what is asked.)`,
          },
        ],
        max_tokens: 400,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      const errorData = await response.json();
      debugLog("❌ API Error Response:", errorData);

      if (errorData?.error?.message?.toLowerCase().includes("rate limit")) {
        return res.status(429).json({ error: "Rate limit exceeded. Try again later." });
      }

      return res.status(500).json({ error: errorData?.error?.message || "API error." });
    }

    const data = await response.json();
    debugLog("✅ API response:", data);

    if (data.choices && data.choices.length > 0) {
      res.json({ reply: data.choices[0].message.content });
    } else {
      res.status(500).json({ error: "No reply from model." });
    }
  } catch (err) {
    console.error("🔥 Fetch failed:", err.message);

    if (err.name === "AbortError") {
      return res.status(504).json({ error: "Request timed out." });
    }

    res.status(500).json({ error: "Groq API call failed." });
  }
});

// Reset endpoint
app.post("/reset", (req, res) => {
  console.log("🔄 Manual reset triggered.");
  res.status(200).send("Reset done");
});

// Start server
app.listen(port, () => {
  console.log(`🚀 Server running at http://localhost:${port}`);
});
