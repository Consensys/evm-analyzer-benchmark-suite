#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
top-level CLI to create an HTML benchmark report
"""

import click
from pathlib import Path
import os, yaml, sys
from jinja2 import select_autoescape, Template
from markdown2 import markdown
import requests
from pygments_lexer_solidity import SolidityLexer
from pygments import highlight
from pygments.formatters import HtmlFormatter

code_root_dir = Path(__file__).parent.resolve()
# Make relative loading work without relative import, which
# doesn't work with main programs
sys.path.insert(0, code_root_dir)

code_dir = Path(__file__).parent.resolve()

RGB_RED    = "rgba(255, 145, 164, .4)"
RGB_GREEN  = "rgba(80, 200, 120, .4)"
RGB_YELLOW = "rgba(253, 195, 83, .4)"
RGB_GREY   = "rgba(128, 128, 128, .4)"

Eval_colors = {
    # Unsupported("rgba(255, 145, 164, .4)", "Unsupported"),
    'False Positive'     : RGB_RED,
    'False Negative'     : RGB_RED,
    'Errored'            : RGB_RED,
    'Wrong Vulnerability': RGB_RED,
    'True Positive'      : RGB_GREEN,
    'True Negative'      : RGB_GREEN,
    'Analysis Failed'    : RGB_YELLOW,
    'Ignored'            : RGB_YELLOW,
    'Timed Out'          : RGB_YELLOW,
    'Too Long'           : RGB_YELLOW,
    'Unconfigured'       : RGB_GREY,
}


def print_html_report(data, project_root_dir, suite):
    """
    Write an HTML analysis report for `suite`

    """

    # Some controller function used in the jinja2 template
    def link_to(link, text):
        return '<a href="%s">%s</a>' % (link, text)

    def markdown_to_html(md):
        return markdown(md)

    def link_issue_result(issue_result):
        return link_to("%s/%s" %
                       ("https://github.com/EthereumAnalysisBenchmarks/evm-analyzer-bench-suites/wiki",
                        issue_result.replace(' ','-')),
                       issue_result)

    def link_source_line(source_url, line_number):
        return link_to("%s#L%d" % (source_url, line_number),
                       'Location')

    def location_info(function_name, line_number, bytecode_offset):
        result = '' if not function_name else 'Function: <code>%s</code>, ' % function_name
        result += 'Line: %s, Bytecode offset: %s' % (line_number, bytecode_offset)
        return result

    def highlight_code(code):
        return highlight(code, SolidityLexer(), HtmlFormatter())

    eval_colors = Eval_colors
    bug_type_links = {}
    for bug_type in eval_colors.keys():
        bug_type_link = (
            "%s/wiki/%s" %
            (data['benchmark_link'], bug_type.replace(' ','-'))
            )
        pass

    html_dir = project_root_dir / 'html'
    suite_path = html_dir / suite
    os.makedirs(suite_path, exist_ok = True)
    jinja2_dir = project_root_dir / 'jinja2'
    template_path = jinja2_dir / 'report_template.html'

    source_code = {}
    bug_type_eval = {}
    base_url_dir_raw = data['benchmark_url_dir']
    base_url_dir = "%s/tree/master/%s" % (data['benchmark_link'], data['benchmark_subdir'])
    bench_data = {}
    for bench_name in data['benchmarks'].keys():
        bench_url_raw = "%s%s%s.sol" % (base_url_dir_raw, os.path.sep, bench_name)
        bench_url = "%s%s%s.sol" % (base_url_dir, os.path.sep, bench_name)
        r = requests.get(bench_url_raw)
        solidity_code = r.text
        source_code[bench_name] = highlight_code(solidity_code)
        bench_data[bench_name] = data['benchmarks'][bench_name]
        bench_data[bench_name]['bench_url'] = bench_url
        pass

    t = Template(open(template_path).read(),
                 autoescape=select_autoescape(['html']),
                 trim_blocks=True)

    # Set up some variables for render
    t.globals = locals()
    html_path = suite_path / "index.html"

    open(html_path, 'w').write(t.render())

import pprint
pp = pprint.PrettyPrinter(indent=4)

# TODO add more analyzers
@click.command()
@click.option('--suite', '-s', type=click.Choice(['Suhabe', 'nssc']),
              default='Suhabe',
              help="Benchmark suite to run; "
              "nscc is an abbreviation for not-so-smart-contracts.")
def generate_benchmark_report(suite):
    analyzer = 'Mythril'
    project_root_dir = code_dir.parent
    suite_dir = project_root_dir / 'benchdata' / suite

    # FIXME: loop over analyzers
    yaml_file = suite_dir / (analyzer + ".yaml")
    with open(yaml_file, 'r') as fp:
        try:
            data = yaml.load(fp)
            # pp.pprint(data)
        except yaml.YAMLError as exc:
            print(exc)
            pass
        pass

    print_html_report(data, project_root_dir, suite)

if __name__ == '__main__':
    generate_benchmark_report()
