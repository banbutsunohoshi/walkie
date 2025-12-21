import os

def main() -> None:
    greeting = os.getenv("WALKIE_GREETING", "Welcome to Walkie!")
    data_dir = os.getenv("WALKIE_DATA_DIR", "/data")
    print(greeting)
    print(f"Data directory: {data_dir}")


if __name__ == "__main__":
    main()
