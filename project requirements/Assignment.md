Assignment: 
Intelligent LLM Agent with Dynamic Tool Selection and Caching Using AWS


Objective:
Design and implement a smart LLM-driven multi agent solution capable of having guardrail & dynamically deciding which tools to execute based on specific instructions.

Requirements
Input Details:

Accept a JSON input containing multiple customer feedback records, each with an optional instructions field that guides the LLM agent.
Example:
{

"feedback_id": "12345",

"customer_name": "John Doe",

"feedback_text": "The product is great, but the delivery was delayed.",

"timestamp": "2025-01-10T10:30:00Z",

"instructions": "Focus on identifying the sentiment and summarizing actionable insights."

}

Agent Functionality:
Multi Agent details
One Agent that is not specific to any particular task, but only responsible to handle User interaction and have guardrail.
Another agent with tool calls (multiple tools)
Dynamic Tool Selection:
The agent should use an LLM (e.g., AWS Bedrock or Groq or OpenAI) to interpret the instructions field and determine which tools to execute.
If no instructions are provided, the agent should execute a default set of tools.

Tool Requirements:
Sentiment Analysis Tool: Perform sentiment scoring (positive, negative, neutral).
Topic Categorization Tool: Categorize feedback into predefined topics (e.g., Product Quality, Delivery, Support).
Keyword Contextualization Tool: Extract context-aware keywords with relevance scores.
Summarization Tool: Generate concise summaries and actionable recommendations.
Caching:
Implement a caching mechanism to store processed requests and their results.
Before processing a new request, check if the request (based on feedback_text and instructions) has been processed before.
If a cached result exists, return it immediately without re-executing the tools.
Store the cache in DynamoDB with the following structure (Extra Credit, Optional):
{

"cache_key": "unique_hash_of_feedback_and_instructions",

"feedback_id": "12345",

"cached_result": {

"sentiment_scores": { "positive": 0.85, "negative": 0.10, "neutral": 0.05 },

"summary": "Delivery delays are causing dissatisfaction. Action: Improve delivery processes."

},

"last_updated": "2025-01-10T10:30:00Z"

}

AWS Integration:
----------------
Core AWS Services:
Use AWS Lambda’s to handle the agent logic, tool orchestration, and caching logic.
(Extra Credit, Optional) Use DynamoDB to store both input/output data and cached results.
Use Lambda as URL to expose the API.

Monitoring:
Log cache hits and misses in CloudWatch for monitoring and optimization insights.

Monitoring and Error Handling:
Log LLM decisions, tool execution metrics, and cache performance(Extra Credit) (e.g., hit/miss ratio) in CloudWatch.
Handle invalid instructions gracefully, with the agent defaulting to executing all tools.

Advanced Requirements:
Instruction Interpretation:
Use the LLM to process complex instructions, such as:
“Identify the key topics and summarize actionable points.”
“Focus only on sentiment analysis and keyword extraction.”
Ensure the LLM can parse and prioritize tasks effectively.

Batch Processing (Extra credit):
Process up to 50 feedback entries in a single request, with dynamic decisions made independently for each record.