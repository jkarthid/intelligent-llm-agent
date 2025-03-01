from setuptools import setup, find_packages

setup(
    name="intelligent-llm-agent",
    version="0.1.0",
    description="Intelligent LLM Agent with Dynamic Tool Selection and Caching",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.28.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
        "groq>=0.4.0",
        "aws-lambda-powertools>=2.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)
