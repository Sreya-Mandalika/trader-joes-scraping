import os
from dotenv import load_dotenv

#setting up MongoDB and collections
load_dotenv(r"C:\Users\Sreya Mandalika\coding-projects\projects-in-programming\env-tester\.env")

hello = print(os.getenv("test"))