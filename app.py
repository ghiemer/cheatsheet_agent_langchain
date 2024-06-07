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

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

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
        model = ChatOpenAI(model="gpt-4")
        search = TavilySearchResults(max_results=2)
        tools = [search]

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
        results.append(response)

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

