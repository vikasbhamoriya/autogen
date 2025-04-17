from flask import Flask, request, render_template
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

app = Flask(__name__)

# ✅ Config for OpenRouter (or OpenAI)
config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": "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",
        "base_url": "https://openrouter.ai/api/v1",
    }
]

# ✅ Agent setup function
def create_agents():
    user = UserProxyAgent(
        name="PatientUI",
        human_input_mode="NEVER",  # Set to "TERMINAL" for debugging
        code_execution_config={"use_docker": False},
    )

    receptionist = AssistantAgent(
        name="Receptionist",
        system_message="You are a hospital receptionist. Help patients schedule appointments and coordinate.",
        llm_config={"config_list": config_list}
    )

    emr_agent = AssistantAgent(
        name="EMRAgent",
        system_message="You retrieve and summarize patient medical records.",
        llm_config={"config_list": config_list}
    )

    billing_agent = AssistantAgent(
        name="BillingAgent",
        system_message="You handle billing queries and validate payments.",
        llm_config={"config_list": config_list}
    )

    return user, receptionist, emr_agent, billing_agent

# ✅ Home page
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Chat endpoint
@app.route('/hospital-chat', methods=['POST'])
def hospital_chat():
    message = request.form.get("message", "")

    # Create agents
    user, receptionist, emr_agent, billing_agent = create_agents()

    # Setup group chat
    groupchat = GroupChat(
        agents=[user, receptionist, emr_agent, billing_agent],
        messages=[],
        max_round=10,
        select_speaker_auto_llm_config={"config_list": config_list},
    )

    manager = GroupChatManager(groupchat=groupchat)

    # User starts the chat (✅ FIXED)
    user.initiate_chat(recipient=manager, message=message)

    # Collect conversation
    all_msgs = [f"{m['name']}: {m['content']}" for m in groupchat.messages]
    return render_template("index.html", conversation=all_msgs, user_input=message)

# ✅ Run the app
if __name__ == '__main__':
    app.run(debug=True)
