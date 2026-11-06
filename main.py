from modules.bot_manager import BotManager
from dotenv import load_dotenv
import os

load_dotenv("keys.env")

def main():
	token = os.getenv("BOT_TOKEN")
	bot_mgr = BotManager(token)
	bot_mgr.start_bot()
	
if __name__ == "__main__":
	main()