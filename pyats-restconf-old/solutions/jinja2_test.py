import jinja2

environment = jinja2.Environment()
interfaces = [{"name":"1"},{"name":"2"},{"name":"3"}]
t = """
{%- for int in interfaces %}
    {%- if int["name"] != "3"%}
name {{ int["name"] }}
    {%- endif %}
{%- endfor %}
"""

template = environment.from_string(t)
print(template.render(interfaces=interfaces))
