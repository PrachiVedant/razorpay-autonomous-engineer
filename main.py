from dotenv import load_dotenv
load_dotenv()

from agents.growth_loop import run_growth_cycle

def main():
    result = run_growth_cycle()
    print(result)


if __name__ == "__main__":
    main()