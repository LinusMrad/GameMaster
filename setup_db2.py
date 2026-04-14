import os
import sys
from dotenv import load_dotenv

print("Python exe:", sys.executable)
print("Nuvarande mapp:", os.getcwd())

load_dotenv()

print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))