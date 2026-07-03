import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Connecting to:", DATABASE_URL)

try:
    with psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row) as conn:
        print("Connection successful!")
        checkpointer = PostgresSaver(conn)
        print("Running checkpointer.setup()...")
        checkpointer.setup()
        print("Setup completed successfully!")
except Exception as e:
    print("Error occurred:", e)
