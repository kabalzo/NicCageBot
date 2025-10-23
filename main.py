import argparse
from bot.bot import create_bot

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Nic Cage Bot')
    parser.add_argument('--mode', choices=['prod', 'test'], 
                       help='Run bot in production or test mode')
    
    args = parser.parse_args()
    
    # Create bot with command line mode override
    bot = create_bot(args.mode)
    bot.run(bot.config.token)

if __name__ == "__main__":
    main()
