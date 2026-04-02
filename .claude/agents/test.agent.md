const { GoogleGenerativeAI } = require("@google/generative-ai");

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

async function runGeminiAgent() {
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });
  
  const prompt = "Your prompt here";
  
  try {
    const result = await model.generateContent(prompt);
    const response = await result.response;
    console.log(response.text());
  } catch (error) {
    console.error("Error:", error);
  }
}

runGeminiAgent();