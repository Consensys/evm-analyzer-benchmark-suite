#!/usr/bin/env python
"""
top-level CLI to create an HTML benchmark report
"""

from pathlib import Path
import yaml
from jinja2 import Template

code_dir = Path(__file__).parent.resolve()

def print_html_doc():
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    template_path = code_dir / 'report_template.html'
    t = Template(open(template_path).read())
    print(t.render(title='testing'))

import pprint
pp = pprint.PrettyPrinter(indent=4)

html_dir = code_dir.parent / 'html'
analyzer = 'mythril'
suite = 'Suhabe'
suite_dir = code_dir.parent / 'benchdata' / suite

# FIXME: loop over analyzers
yaml_file = suite_dir / (analyzer + ".yaml")
with open(yaml_file, 'r') as stream:
    try:
        data = yaml.load(stream)
        # pp.pprint(data)
    except yaml.YAMLError as exc:
        print(exc)

print_html_doc()
