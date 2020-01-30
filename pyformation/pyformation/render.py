from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('pyformation', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def render_file(template_name, vars, project_path):
    try:
        template = env.get_template(template_name)
    except Exception as e:
        print("Find Template Error {}".format(e))
        return False
    try:
        rendered = template.render(vars=vars)
    except Exception as e:
        print("Template Render Error: {}".format(e))
        return False
    try:
        file_path = '{}{}'.format(project_path, template_name)
        with open(file_path, 'w') as f:
            f.write(rendered)
    except Exception as e:
        print('Save Template Error {}'.format(e))
        return False
    return True
