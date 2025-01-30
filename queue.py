from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from whatsapp import send
import sqlite3
import time
import json
import os    

class Params(BaseModel):
    input: Any

class Content(BaseModel):
    id: Optional[int] = None
    input: Optional[str] = None
    output: Optional[str] = None

def get_sql_conn():
    return sqlite3.connect('local.db')

conn = get_sql_conn()
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS contents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input TEXT NULL,
        output TEXT NULL
    )
''')
conn.commit()
cursor.close()
conn.close()

def insert(content: Content):
    conn = get_sql_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contents (input, output)
        VALUES (?, ?)
    ''', (content.input, content.output))
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def update(content: Content):
    conn = get_sql_conn()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE contents SET input = ?, output = ? WHERE id = ?
    ''', (content.input, content.output, content.id))
    conn.commit()
    cursor.close()
    conn.close()

def select_by_id(content_id: int):
    content_id = int(content_id)
    conn = get_sql_conn()
    cursor = conn.cursor()
    if content_id > 0:
        cursor.execute('''
            SELECT id, input, output FROM contents WHERE id = ?
        ''', (content_id,))
    else:
        cursor.execute('''
                SELECT id, input, output FROM contents ORDER BY id DESC LIMIT 10
        ''')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def select_by_last_id():
    conn = get_sql_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, input, output FROM contents WHERE output IS NULL ORDER BY id DESC LIMIT 1
    ''')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

app = FastAPI()

@app.post("/push")
def push_message(content: Content):
    try:
        conn = get_sql_conn()
        cursor = conn.cursor()
        if content.output is not None:
            result = select_by_last_id()
            if result:
                output = content.output
                content = Content(id=result[0], input=result[1], output=output)
                cursor.execute('''
                    UPDATE contents SET input = ?, output = ? WHERE id = ?
                ''', (content.input, content.output, content.id))
                conn.commit()
                content.id = content.id
            else:
                cursor.execute('''
                    INSERT INTO contents (output)
                    VALUES (?)
                ''', (content.output,))
                conn.commit()
                content.id = cursor.lastrowid
        elif content.input:
            cursor.execute('''
                INSERT INTO contents (input, output)
                VALUES (?, ?)
            ''', (content.input, content.output))
            conn.commit()
            content.id = cursor.lastrowid
            send(content.input)
        cursor.close()
        conn.close()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing message: {e}")

@app.get("/pull")
def pull_messages(content_id: str):    
    
    messages = select_by_id(content_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Content not found")
    content = Content(id=messages[0], input=messages[1], output=messages[2]).model_dump()
    return JSONResponse(content)

@app.post("/whatsapp")
def start_conversation(content: Content, timeout: int = 30):

    content = push_message(content)
    time.sleep(2)
    content_id = content.id
    start_time = time.time()
    while True:
        try:
            messages = select_by_id(content_id)
            if messages[2]:
                content = Content(id=messages[0], input=messages[1], output=messages[2])
                return JSONResponse(content.model_dump())
            time.sleep(1)
        except:
            break
    
    content = Content(id=messages[0], input=messages[1], output='')
    return JSONResponse(content.model_dump())

@app.get("/openai")
def gpt_conversation(input: Any, request: Request):
    """Handles GPT conversation requests."""
    # print(input, type(input), request)
    try:
        if isinstance(input, dict):
            input_text = input.get("input")
        else:
            params = json.loads(input) 
            input_text = params.get('input')
    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"Invalid JSON: {e}"})
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return JSONResponse({"error": "OPENAI_API_KEY environment variable not set"})


    client = OpenAI(api_key=api_key)
    SYSTEM = """You are a personal finance advisor, providing guidance on budgeting, saving, investing, and managing debt. Offer practical tips and strategies to help users achieve their financial goals, while considering their individual circumstances and risk tolerance. Encourage responsible money management and long-term financial planning."""

    try:
        completion = client.chat.completions.create(
        model="gpt-4o-x",
        messages=[
            {"role": "system", "content": SYSTEM}, # Changed role to system for clarity
            {"role": "user", "content": input_text}
        ]
        )
        
        output = completion.choices[0].message.content
    except:
        output = "Output"

    content = Content(input=input_text, output=output)
    
    return JSONResponse(content.model_dump())

# python code to run
# uvicorn pubsub:app --reload --port 5051