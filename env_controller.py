import os
import dotenv

def set_env_variable(key, value):
    env_file = dotenv.find_dotenv()

    # Check if the key already exists in the .env file
    with open(env_file, "r") as file:
        lines = file.readlines()

    # Update the variable if it exists, otherwise add it
    with open(env_file, "w") as file:
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                found = True
            else:
                file.write(line)
        if not found:
            file.write(f"{key}={value}\n")


def get_env(key):
    if os.getenv(key):
        return os.getenv(key)
    else:
        return False

def reload_env(env_path):
    dotenv.load_dotenv(env_path)