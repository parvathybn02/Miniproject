# SmartStudy AI

An intelligent learning partner powered by AI.

## Features
- AI-Powered Summarization
- Flashcard Generation
- Document Analysis
- Study Planning

## Docker Setup
The project is containerized. To run using Docker:
1. Build the image: `docker build -t study-platform .`
2. Run the container: `docker run -d -p 5000:5000 --name study-app --env-file .env study-platform`
