import dotenv
import os
from agent import TripPlannerAgent

def main():
    dotenv.load_dotenv()
    agent = TripPlannerAgent()
    agent.chat_loop()

if __name__ == "__main__":
    main()