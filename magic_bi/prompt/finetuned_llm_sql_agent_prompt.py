select_tables_prompt_template = \
'''{table_descriptions}

[User Question]:
    {user_question}

Identify the tables from the Tables that you think may answer the User Question.
Output the table names in json list format directly without any explanation.'''

generate_sql_prompt_template = \
'''[Env Info]:
    {env_info}

{relevant_table_descriptions}

[User Question]:
    {user_question}

Based on the above, generate sql that answer the user question. Directly output the SQL statement without any explanation.'''

prompt_template_make_sql_output_human_readable = \
'''[USER INPUT]:
    {user_input}

[RETRIEVED DATA]:
    {retrieved_data}

根据抽取的数据用简体中文回答用户问题，不要提类似于“根据”的词。'''