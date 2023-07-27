import pyodbc
import re
import pandas as pd
import openai
import streamlit as st


st.title("Data Analysis Using LLM V1")

conn = None  # Initialize conn to None
code = None

def connect_to_database(server, database, username, password):
    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as e:
        st.error(f"Error connecting to the database: {str(e)}")
        return None

def my_func(prompt):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    a = completion.choices[0].message.content
    b = a.replace("\n", " ")
    return b


def code_extract(b):
    try:
        string = b
        code_pattern = r"```sql(.*?)```"
        matches = re.findall(code_pattern, string, re.DOTALL)
        if string.lower().startswith(("select", "SELECT")):
            code = string
        else:
            if matches:
                code = matches[0].strip()
            else:
                code_pattern = r"```(.*?)```"
                matches = re.findall(code_pattern, string, re.DOTALL)
                code = matches[0].strip()
    except IndexError as e:
        st.error(f" Apologiese AI didn't given code Please check the prompt and below AI output {str(b)}")

    return code


server = st.text_input("Please enter the server name")
database = st.text_input("Please enter the database name")
username = st.text_input("please enter the user name")
password = st.text_input("Please enter the password", type="password")
connect_button = st.button("Connect")
if connect_button:
    conn = connect_to_database(server, database, username, password)
    if conn is not None:
        #st.write(conn)
        st.success("Successfully connected to the database!")
openai.api_key = st.text_input("Please enter the key")
pre_prompt = st.text_input("Please enter the pre_prompt")
prompt = st.text_input("How can I help you")
if st.button("Check the code"):
    if prompt:
        prompt = prompt + pre_prompt
        with st.spinner("Please Wait....."):
            try:
                query = my_func(prompt)
                code = code_extract(query)
                st.write(code)
                if conn is None:
                    conn = connect_to_database(server, database, username, password)
                df = pd.read_sql_query(code, conn)
                st.write(df)
            except (pd.errors.DatabaseError, pyodbc.DatabaseError) as e:
                # Handle the database-related error
                st.error(f" There is an error in AI generated Query, "
                         f" Please re-run once if issue still persists then check the code and redisgn the prompt accordingly and Run: {str(e)}")

            except Exception as e:
                # Handle other unexpected exceptions
                st.error(f" opean AI running busy ,Apoligies Please try Again  {str(e)}")
