import subprocess
import sys
import os
import logging
import configparser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("game_launcher.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GameLauncher")

def run_game_script(script_path):
    if not os.path.isfile(script_path):
        logger.error(f"File '{script_path}' does not exist!")
        return

    if not script_path.endswith('.py'):
        logger.warning(f"'{script_path}' may not be a Python script.")

    try:
        logger.info(f"Launching game script: {script_path}")
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            close_fds=True
        )
        logger.info("Game script launched successfully. Capturing logs...")
        for line in process.stdout:
            logger.info(line.strip())

        process.wait()
        logger.info("Game script has finished execution.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('mota.ini')
    target_script = config.get('Mota', 'Script')
    run_game_script(target_script)
