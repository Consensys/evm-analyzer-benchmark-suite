#!/bin/bash
# - Run report formatter (runner/report.py) over all benchmarks
# - copy the result html
# - update report site
set -e
cd $(dirname ${BASH_SOURCE[0]})
mydir=$(pwd)
cd $mydir
reports_dir=../../EtheriumAnalysisBenchMarks.github.io
PYTHON=${PYTHON:-python}
for report in Suhabe nssc; do
    $PYTHON ../runner/report.py -s $report
    cp -vp ../html/$report/index.html $reports_dir/$report/index.html
done
cd $reports_dir
git commit -m"$(date) Update" .
git push
