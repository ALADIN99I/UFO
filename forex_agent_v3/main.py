import configparser
from src.live_trader import LiveTrader

def main():
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    live_trader = LiveTrader(config)
    live_trader.run_single_cycle()

if __name__ == "__main__":
    main()
