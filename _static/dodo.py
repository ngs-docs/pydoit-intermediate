import jinja2
import os

from doit.tools import run_once
from doit.task import clean_targets

DATA_URLS = ['https://s3.amazonaws.com/pydoit-intermediate/Melee_data.csv.document.md.tpl',
             'https://s3.amazonaws.com/pydoit-intermediate/Melee_data.csv.gz']

def task_download_data():

    def print_url(URL):
        print 'File was retrieved from: {0}'.format(URL)

    for URL in DATA_URLS:
        target = os.path.basename(URL)
        yield {'name': 'download:{0}'.format(target),
               'actions': ['curl -OL {0}'.format(URL)],
               'targets': [target],
               'uptodate': [run_once],
               'clean': [clean_targets, (print_url, [URL])]}


def task_gunzip_data():
    return {'actions': ['gunzip -c %(dependencies)s > %(targets)s'],
            'targets': ['Melee_data.csv'],
            'file_dep': ['Melee_data.csv.gz']}


def task_plot_heatmap():

    def do_plot(dependencies, targets):
        import matplotlib.pyplot as plt
        import pandas as pd
        import seaborn as sns

        data = pd.read_csv(list(dependencies)[0], index_col=0)
        clst = sns.clustermap(data, linewidths=.5, figsize=(8, 8), square=True,
                              method='ward', z_score=0, row_cluster=False)
        # I'm a stickler, so rotate the labels nicely
        plt.setp(clst.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
        plt.setp(clst.ax_heatmap.xaxis.get_majorticklabels(), rotation=90)
        clst.savefig(targets[0])

    return {'actions': [do_plot],
            'file_dep': ['Melee_data.csv'],
            'targets': ['Melee_data.csv.heatmap.pdf']}

def task_build_markdown_file():

    def do_build(targets):
        
        with open(targets[0] + '.tpl') as fp:
            template = jinja2.Template(fp.read())

        with open(targets[0], 'wb') as fp:
            fp.write(template.render(author='Your Name',
                                     affiliation='Your Institution',
                                     date='Jan 20, 2016',
                                     heatmap_filename='Melee_data.csv.heatmap.pdf'))

    return {'actions': [do_build],
            'file_dep': ['Melee_data.csv.heatmap.pdf',
                         'Melee_data.csv.document.md.tpl'],
            'targets': ['Melee_data.csv.document.md'],
            'clean': [clean_targets]}

def task_pandoc():

    cmd = 'pandoc -r markdown+yaml_metadata_block+startnum+fancy_lists'\
          ' -s -S %(dependencies)s -o %(targets)s'

    return {'actions': [cmd],
            'file_dep': ['Melee_data.csv.document.md'],
            'targets': ['Melee_data.csv.document.pdf'],
            'clean': [clean_targets]}
