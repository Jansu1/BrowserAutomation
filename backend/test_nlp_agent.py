from nlp_agent import NLPAgent

agent = NLPAgent()

while True:
    user = input("You: ")
    if user.lower() in ["exit", "quit"]:
        break
    response = agent.process_input(user)
    print("Agent:", response)
