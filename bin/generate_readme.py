#!/usr/bin/env python3

###############################################################################
#
#    Copyright (C) 2023 Ben Woodcroft
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

__author__ = "Ben Woodcroft"
__copyright__ = "Copyright 2023"
__credits__ = ["Ben Woodcroft"]
__license__ = "GPL3"
__maintainer__ = "Ben Woodcroft"
__email__ = "benjwoodcroft near gmail.com"
__status__ = "Development"

import argparse
import logging
import sys
import os
from urllib import request
import polars as pl
from pytablewriter import MarkdownTableWriter

sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')] + sys.path

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--debug', help='output debug information', action="store_true")
    #parent_parser.add_argument('--version', help='output version information and quit',  action='version', version=repeatm.__version__)
    parent_parser.add_argument('--quiet', help='only output errors', action="store_true")

    parser = argparse.ArgumentParser(parents=[parent_parser])
    subparsers = parser.add_subparsers(title="Sub-commands", dest='subparser_name')

    cluster_description = 'Cluster bins and assembled contigs'
    cluster_parser = subparsers.add_parser('cluster')
    cluster_parser.add_argument(
        '--bin_directories', nargs='+', metavar='DIR [DIR ..]',
        help="Directories containing FASTA files of bins", required=True)

    args = parser.parse_args()

    # Setup logging
    if args.debug:
        loglevel = logging.DEBUG
    elif args.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # CSV url generated in the previous step (should look similar to the one below, which I generated for the dataset submission form responses)
    download_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSgbEXINkhCDhOewVs3S8QinggdILjT__69CmWL1aBQYlVCP9jKSz_XziTeHVL1Nl6wshBkxsiruFwK/pub?gid=0&single=true&output=tsv"

    # download the file contents into a (large) string variable
    logging.info("Downloading CSV file.")
    with request.urlopen(download_url) as incoming_download:
        sheet = pl.read_csv(incoming_download.read(), separator='\t', comment_char='#')

    logging.info("Downloaded CSV file.")

    values = []

    headers = ['Tool','Description','Developers','Citation']
    
    for row in sheet.rows(named=True):
        name = row['Tool Name (e.g. GraftM)']
        link = row['Link to Tool']
        if link is None or 'http' not in link:
            logging.debug("Skipping tool %s because it has no link.", name)
            continue

        cite = row['Citation/Status']
        if cite is None or not 'http' in cite:
            cite = f''
        
        values.append([
            f"[{name}]({row['Link to Tool']})",
            row['1-sentence description of what it does'],
            row['Developers'],
            cite
        ])

    writer = MarkdownTableWriter(
        table_name="EMERGE tools",
        headers=headers,
        value_matrix=values,
    )

    md_table = writer.dumps()

    with open(os.path.join(os.path.dirname(__file__), '..', 'profile', 'README.md'), 'w') as readme:
        print('''# EMERGE Biology Integration Institute

Predictive understanding of ecosystem response to change has become a pressing societal need in the Anthropocene, and requires integration across disciplines, spatial scales, and timeframes. Developing a framework for understanding how different biological systems interact over time is a major challenge in biology. The National Science Foundation-funded EMergent Ecosystem Responses to ChanGE (EMERGE) Biology Integration Institute aims to develop such a framework by integrating research, training, and high-resolution field and laboratory measurements across 15 scientific subdisciplines–including ecology, physiology, genetics, biogeochemistry, remote sensing, and modeling–across 14 institutions, in order to understand ecosystem-climate feedbacks in Stordalen Mire, a thawing permafrost peatland in arctic Sweden. Rapid warming in the Arctic is driving permafrost thaw, and new availability of formerly-frozen soil carbon for cycling and release to the atmosphere, representing a potentially large but poorly constrained accelerant of climate change. This material is based upon work supported by the National Science Foundation under Grant Number 2022070.

Listed below are a number of the tools that members have developed for better understanding and integration of these datasets.

''', file=readme)

        readme.write(md_table)

