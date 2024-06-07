from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import logging
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def web_search(query):
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='g'):
        links = g.find_all('a')
        if links:
            link = links[0]['href']
            results.append(link)
    return results[:5]

@app.route('/query', methods=['POST'])
def query_agent():
    try:
        data = request.json
        if not data or 'question' not in data:
            return jsonify({"status": "error", "message": "Invalid input"}), 400

        question = data.get('question')
        language = data.get('language', 'en')
        config = {"configurable": {"thread_id": data.get('thread_id', 'default_thread')}}
        results = []

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        model = ChatOpenAI(model="gpt-4o")
        search = TavilySearchResults(max_results=2)
        tools = [search]

        # Web search for additional information
        web_results = web_search(question)
        additional_info = " ".join([f"Source: {url}" for url in web_results])

        # Define the prompt template with language support
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(f"You are an AI assistant specialized in providing accurate and detailed information on various topics, especially in technology and blockchain. Please respond in {language}."),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        )

        # Create the agent executor
        agent_executor = LLMChain(
            llm=model,
            prompt=prompt,
            memory=memory,
            verbose=True
        )

        response = agent_executor.predict(question=question)
        results.append(response + "\n\n" + additional_info)

        cheatsheet = summarize_results(results)
        file_name = save_as_markdown(cheatsheet, config.get('output_folder', './cheatsheets/'), language)

        return jsonify({"status": "success", "results": results, "file": file_name})

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def summarize_results(results):
    try:
        cheatsheet = "# Cheatsheet\n\n"
        for result in results:
            cheatsheet += result + "\n\n"
        return cheatsheet
    except Exception as e:
        logging.error(f"An error occurred while summarizing results: {str(e)}")
        return "# Cheatsheet\n\nError in summarizing results.\n\n"

def save_as_markdown(content, output_folder, language):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"cheatsheet_{language}_{timestamp}.md"
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, "w") as file:
            file.write(content)
        return file_name
    except Exception as e:
        logging.error(f"An error occurred while saving the markdown file: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

