# Intelligent LLM Agent with Dynamic Tool Selection and Caching

This project implements a smart LLM-driven multi-agent solution capable of having guardrails and dynamically deciding which tools to execute based on specific instructions.

## Features

- **Dynamic Tool Selection**: Automatically selects the appropriate tools based on customer feedback
- **Multi-Agent Architecture**: Separates interaction logic from tool execution
- **Caching System**: Improves performance and reduces costs by caching processed requests
- **AWS Integration**: Seamlessly integrates with AWS services for scalability and reliability
- **Comprehensive Testing**: Ensures reliability and correctness of all components
- **CI/CD Pipeline**: Automates testing, building, and deployment

## Architecture

The system consists of two main agents:
1. **Interaction Agent**: Handles user interaction, applies guardrails, and interprets instructions to determine which tools to execute
2. **Tool Agent**: Executes specific tools based on instructions from the Interaction Agent

### Tools
- **Sentiment Analysis Tool**: Analyzes the sentiment of customer feedback
- **Topic Categorization Tool**: Categorizes customer feedback into predefined topics
- **Keyword Contextualization Tool**: Extracts context-aware keywords from customer feedback
- **Summarization Tool**: Generates concise summaries and actionable recommendations

### Caching
The system implements a caching mechanism to store processed requests and their results, improving performance for repeated requests. Two caching strategies are supported:
- **Memory Cache**: In-memory cache for fast access
- **DynamoDB Cache**: Persistent cache for storing processed requests

### AWS Integration
- **AWS Lambda**: Processes customer feedback and invokes agents and tools
- **DynamoDB**: Stores cached results (optional)
- **CloudWatch**: Monitors performance and logs events

## Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Terraform installed (version 1.0.0+)
- Python 3.9+
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intelligent-llm-agent.git
   cd intelligent-llm-agent
   ```

2. **Set up the environment**
   ```bash
   setup_all.bat
   ```

3. **Run the application locally**
   ```bash
   run_in_venv.bat
   ```

4. **Deploy to AWS**
   ```bash
   deploy_from_venv.bat
   ```

See the [deployment checklist](https://github.com/jkarthid/intelligent-llm-agent/wiki/deployment_checklist) for detailed deployment instructions.

## API Usage

The API accepts JSON input containing customer feedback records with optional instructions.

Example:
```json
{
  "feedback_id": "12345",
  "customer_name": "John Doe",
  "feedback_text": "The product is great, but the delivery was delayed.",
  "timestamp": "2025-01-10T10:30:00Z",
  "instructions": "Focus on identifying the sentiment and summarizing actionable insights."
}
```

Example Response:
```json
{
  "feedback_id": "12345",
  "results": {
    "sentiment": {
      "overall": "mixed",
      "product": "positive",
      "delivery": "negative"
    },
    "topics": ["product quality", "delivery speed"],
    "keywords": ["great", "delayed", "product", "delivery"],
    "summary": "Customer is satisfied with the product quality but experienced delivery delays.",
    "recommendations": ["Investigate delivery process", "Follow up with customer about delivery experience"]
  },
  "processed_timestamp": "2025-01-10T10:35:00Z"
}
```

See the [API documentation](https://github.com/jkarthid/intelligent-llm-agent/wiki/api) for more details.

## Development

### Project Structure
```
intelligent-llm-agent/
├── src/
│   ├── agents/         # Agent implementations
│   ├── tools/          # Tool implementations
│   ├── cache/          # Caching implementations
│   ├── aws/            # AWS integration
│   └── utils/          # Utility functions
├── tests/              # Test files
├── infrastructure/     # Terraform configuration
├── ci-cd/              # CI/CD configuration
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

### Available Scripts

- **setup_venv.bat**: Sets up the virtual environment
- **check_structure.bat**: Checks project structure
- **check_aws.bat**: Checks AWS configuration
- **run_all_tests.bat**: Runs all tests
- **run_tests.bat**: Runs unit tests
- **run_lint.bat**: Runs linting checks
- **format_code.bat**: Formats the code
- **run_app.bat**: Runs the application locally
- **run_in_venv.bat**: Runs the application in the virtual environment
- **deploy_from_venv.bat**: Deploys to AWS
- **update_docs.bat**: Updates documentation
- **run_report.bat**: Generates project report
- **clean_project.bat**: Cleans up the project
- **create_release.bat**: Creates a new release

See the [scripts guide](https://github.com/jkarthid/intelligent-llm-agent/wiki/scripts_guide) for more details.

### Configuration

The system can be configured using environment variables:

- **LLM_PROVIDER**: Specifies the LLM provider (e.g., OpenAI, Anthropic)
- **LLM_MODEL**: Specifies the model to use for the LLM
- **USE_CACHE**: Flag to determine if caching should be used
- **CACHE_TYPE**: Type of cache to use (memory or DynamoDB)
- **AWS_REGION**: Specifies the AWS region for resource deployment
- **DYNAMODB_TABLE**: Specifies the DynamoDB table for caching

## Documentation

- [Project Overview](https://github.com/jkarthid/intelligent-llm-agent/wiki/project_summary)
- [Architecture Documentation](https://github.com/jkarthid/intelligent-llm-agent/wiki/architecture)
- [API Documentation](https://github.com/jkarthid/intelligent-llm-agent/wiki/api)
- [Deployment Checklist](https://github.com/jkarthid/intelligent-llm-agent/wiki/deployment_checklist)
- [Troubleshooting Guide](https://github.com/jkarthid/intelligent-llm-agent/wiki/troubleshooting)
- [Performance Optimization](https://github.com/jkarthid/intelligent-llm-agent/wiki/performance_optimization)
- [Project Status](https://github.com/jkarthid/intelligent-llm-agent/wiki/project_status)
- [Contributing Guidelines](CONTRIBUTING.md)

## License
[MIT](LICENSE)

## Acknowledgements
- OpenAI for GPT models
- Anthropic for Claude models
- AWS for cloud infrastructure
- All contributors to this project
