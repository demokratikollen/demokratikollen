# -*- coding: utf-8 -*-

import argparse
import logging
import os
import os.path
import zipfile

import data_import.data_import

DEFAULT_CLEANED_PREFIX = 'cleaned_'

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(prog='data')
    subparsers = parser.add_subparsers()

    setup_download_parser(subparsers.add_parser('download'))
    setup_clean_parser(subparsers.add_parser('clean'))

    args = parser.parse_args()

    args.func(args)



def setup_download_parser(parser):

    def download(args):
        with open(args.urls_file, encoding='utf-8') as f:
            urls = f.readlines()
            data_import.download(urls, args.dir, overwrite=args.overwrite)

    parser.add_argument('urls_file', type=str,
        help='Path of file with URLs of file(s) to process (one URL per line).')
    parser.add_argument('dir', type=str, help='Output directory.')
    parser.add_argument('--overwrite', '-o' , action='store_true',
        help='Enable to overwrite files.')
    parser.set_defaults(func=download)


def setup_clean_parser(parser):

    def clean(args):
        if os.path.isdir(args.path):
            paths = filter(
                os.path.isfile, 
                (os.path.join(args.path, f) for f in os.listdir(args.path)))
        else:
            paths = [args.path]

        for path in paths:
            try:
                filename = os.path.basename(path)

                data_import.clean(path, args.prefix, outdir=args.outdir)

            except data_import.CannotCleanException as e:
                if not args.silent:
                    logger.warning('Skipping {0} '
                        'because there is no cleaning action for it.'.format(filename))

        
    parser.add_argument('path', type=str, help='Path to a file or directory of files to process.')
    parser.add_argument('--outdir', '-o', type=str, default=None,
        help='Directory to put cleaned file in. Default: same as input file.')
    parser.add_argument('--prefix', type=str, default=DEFAULT_CLEANED_PREFIX, 
        help=('A prefix to add to the filename of the processed file. '
            'Default: {0}'.format(DEFAULT_CLEANED_PREFIX))
        )
    parser.add_argument('--silent', '-s', action='store_true',
        help='Be silent about files that cannot be cleaned.')
    parser.set_defaults(func=clean)


if __name__ == '__main__':
	main()