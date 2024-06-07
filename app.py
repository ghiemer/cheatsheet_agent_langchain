from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import logging
import os

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
        config = {"configurable": {"thread_id": data.get('thread_id', 'default_thread')}}
        results = []

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        model = ChatOpenAI(model="gpt-4")
        search = TavilySearchResults(max_results=2)
        tools = [search]
        agent_executor = LLMChain(
            llm=model,
            memory=memory,
            prompt=ChatPromptTemplate(
                messages=[
                    SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessagePromptTemplate.from_template("{question}")
                ]
            ),
            verbose=True
        )

        response = agent_executor.predict(question=question)
        results.append(response)

        cheatsheet = summarize_results(results)
        save_as_markdown(cheatsheet, config.get('output_folder', './cheatsheets/'))

        return jsonify({"status": "success", "results": results})

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

def save_as_markdown(content, output_folder):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        with open(os.path.join(output_folder, "cheatsheet.md"), "w") as file:
            file.write(content)
    except Exception as e:
        logging.error(f"An error occurred while saving the markdown file: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

