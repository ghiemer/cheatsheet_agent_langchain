# LangChain Agent

This project implements a Flask-based API service capable of searching for technology information and documentation and summarizing it in Markdown format. The information is retrieved and processed using OpenAI GPT-4o and a web search function.

## Table of Contents
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Options](#options)
- [Examples](#examples)
- [Docker Commands](#docker-commands)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Authors](#authors)

## Installation

1. **Clone the Repository**
    ```sh
    git clone <repository-url>
    cd langchain_agent
    ```

2. **Create and Activate a Virtual Environment**
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4. **Create the `.env` File**
    Create a `.env` file in the project directory and add the following environment variables:
    ```
    OPENAI_API_KEY=your_openai_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

## Environment Variables

- `OPENAI_API_KEY`: Your API key for OpenAI.
- `TAVILY_API_KEY`: Your API key for Tavily.

## Usage

1. **Start the Flask Server**
    ```sh
    python app.py
    ```

2. **Send a Request**
    Use `curl` or a tool like Postman to send requests to the API.

## API Endpoints

### POST `/query`

This endpoint accepts a question and returns a detailed answer along with a Markdown file.

- **Request Body** (JSON):
    ```json
    {
      "question": "What is LangChain?",
      "thread_id": "example_thread",
      "language": "en"
    }
    ```

- **Response** (JSON):
    ```json
    {
      "status": "success",
      "results": ["LangChain is a project..."],
      "file": "cheatsheet_en_20240607_102119.md"
    }
    ```

## Options

- **`question`**: The question to be answered.
- **`thread_id`**: (Optional) An ID that identifies the thread or context of the request.
- **`language`**: (Optional) The language of the response. Default is English (`en`).

## Examples

### Example Request with `curl`

```sh
curl -X POST http://localhost:5001/query \
     -H "Content-Type: application/json" \
     -d '{
           "question": "What is LangChain?",
           "thread_id": "example_thread",
           "language": "en"
         }'
```

### Example Response

```json
{
  "status": "success",
  "results": ["LangChain is a blockchain project..."],
  "file": "cheatsheet_en_20240607_102119.md"
}
```

## Docker Commands

### Stop and Remove Containers

```sh
docker compose down
```

### Rebuild and Start Containers

```sh
docker compose up --build
```

### Docker Setup

1. **Build the Docker Image**
    ```sh
    docker build -t langchain_agent .
    ```

2. **Run the Docker Container**
    ```sh
    docker run -d -p 5000:5000 --env-file .env langchain_agent
    ```

### Docker Compose

Use `docker-compose` for easier management:

1. **Start the Containers**
    ```sh
    docker compose up --build
    ```

2. **Stop the Containers**
    ```sh
    docker compose down
    ```

## Troubleshooting

If issues arise, check the log files and ensure all environment variables are set correctly. Use logging to get detailed information about errors.

## License

This project is licensed under the MIT License. For more details, see the LICENSE file.

## Authors

- [Your Name](https://github.com/yourusername)
- Additional Contributors

