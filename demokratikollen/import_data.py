# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import os
import os.path
import zipfile
import time

import psycopg2

from demokratikollen.data_import import data_import
import demokratikollen.core.utils.postgres as pg_utils
import demokratikollen.core.utils.misc as misc_utils

DEFAULT_CLEANED_PREFIX = 'cleaned_'

logger = logging.getLogger(__name__)

def main():
    """Command line interface for importing data from riksdagen."""

    parser = argparse.ArgumentParser(prog='import_data')
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    setup_download_parser(subparsers.add_parser('download',
        help=('Download files from URLs in a file.')))
    setup_unpack_parser(subparsers.add_parser('unpack',
        help='Unpack a zip file or all the zip files in a directory.'))
    setup_clean_parser(subparsers.add_parser('clean',
        help=('Clean errors in indata files. Note: Cleaning actions are chosen depending on '
            "the file name of the indata file, so don't change names of indata files if "
            "you are not sure what you are doing.")))
    setup_wipe_parser(subparsers.add_parser('wipe',
        help='Wipe the riksdagen database and create empty tables.'))
    setup_execute_parser(subparsers.add_parser('execute',
        help='Execute statements from an .sql file or all the .sql files in a directory.'))

    args = parser.parse_args()

    try:
        logger.info('Running {0}.'.format(str(args.func.__name__)))
        args.func(args)
        logger.info('Successfully finished.')
    except psycopg2.ProgrammingError as e:
        logger.error('Terminated because database query failed: {0}'.format(str(e).rstrip()))
    except KeyboardInterrupt as e:
        logger.info('Terminated because of user interrupt.')
    except Exception as e:
        logger.error('Terminated because of an unhandled exception.')
        logger.debug(e, exc_info=sys.exc_info())



def setup_download_parser(parser):
    """Setup a subparser for the download subcommand."""

    def download(args):
        with open(args.urls_file, encoding='utf-8') as f:
            urls = f.readlines()
            data_import.download(urls, args.outdir, overwrite=args.overwrite)

    parser.add_argument('urls_file', type=str,
        help='Path of file with URLs of file(s) to process (one URL per line).')
    parser.add_argument('outdir', type=str, help='Output directory.')
    parser.add_argument('--overwrite', '-o' , action='store_true',
        help='Enable to overwrite files.')
    parser.set_defaults(func=download)


def setup_unpack_parser(parser):
    """Setup a subparser for the unpack subcommand."""

    def unpack(args):
        if os.path.isdir(args.path):
            paths = filter(
                os.path.isfile, 
                (os.path.join(args.path, f) for f in os.listdir(args.path)))
        else:
            paths = [args.path]

        for path in paths:
            if not zipfile.is_zipfile(path):
                logger.debug('Skipping {0} because it is not a zipfile.'.format(path))
                continue

            outdir = args.outdir if args.outdir else os.path.dirname(path)

            with zipfile.ZipFile(path) as archive:
                for member in archive.namelist():
                    logger.info(
                        'Extracting from {0}: {1}'.format(path, os.path.join(outdir, member)))
                    archive.extract(member, path=outdir)

            if args.remove:
                logger.info('Removing {0}.'.format(path))
                os.remove(path)

    parser.add_argument('path', type=str, help='Path to a file or directory of files to unpack.')
    parser.add_argument('outdir', type=str, default=None,
        help='Directory to put unpacked file(s) in.')
    parser.add_argument('--remove', '-r', action='store_true',
        help='Remove the archive(s) after unpacking.')
    parser.set_defaults(func=unpack)


def setup_clean_parser(parser):
    """Setup a subparser for the clean subcommand."""

    def clean(args):
        if os.path.isdir(args.path):
            paths = filter(
                os.path.isfile, 
                (os.path.join(args.path, f) for f in os.listdir(args.path)))
        else:
            paths = [args.path]

        for path_in in paths:
            try:
                filename = os.path.basename(path_in)
                path_out = os.path.join(args.outdir, args.prefix + filename)

                logger.info('Cleaning {0}.'.format(path_in))
                
                t0 = time.time()

                data_import.clean(path_in, path_out, overwrite=args.overwrite)

                t1 = time.time()
                logger.info('Cleaned {0} in {1:.1f} seconds.'.format(filename, t1-t0))

                if args.remove:
                    logger.info('Removing {0}.'.format(path_in))
                    os.remove(path_in)

            except data_import.CannotCleanException as e:
                if not args.silent:
                    logger.warning('Skipping {0} '
                        'because there is no cleaning action for it.'.format(filename))
            except FileExistsError as e:
                logger.warning('Skipping {0} because the output file already exists. '
                    'Hint: use the --overwrite option?'.format(filename))

        
    parser.add_argument('path', type=str, help='Path to a file or directory of files to process.')
    parser.add_argument('outdir', type=str, default=None,
        help='Directory to put cleaned file(s) in.')
    parser.add_argument('--prefix', type=str, default=DEFAULT_CLEANED_PREFIX, 
        help=('A prefix to add to the filename of the processed file. '
            'Default: {0}'.format(DEFAULT_CLEANED_PREFIX)))
    parser.add_argument('--silent', '-s', action='store_true',
        help='Be silent about files that cannot be cleaned.')
    parser.add_argument('--overwrite', '-o', action='store_true',
        help='Overwrite output files that already exist.')
    parser.add_argument('--remove', '-r', action='store_true',
        help='Remove the source file(s) after cleaning.')
    parser.set_defaults(func=clean)


def dropall(conn):
    """Drop all tables in a postgresql database.

    To be precise, drop all tables where table_schema = 'public'.

    Args:
        conn (psycopg2.Connection): A connection to the database.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT table_schema,table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            logger.info('Dropping table: {0}'.format(row[1]))
            cur.execute("drop table {} cascade".format(row[1]))

def setup_wipe_parser(parser):
    """Setup a subparser for the wipe subcommand."""

    def wipe(args):
        db_url = pg_utils.database_url(which='riksdagen')
        with psycopg2.connect(db_url) as conn:

            logger.info('Dropping all tables.')
            dropall(conn)
            logger.info('Creating tables.')
            pg_utils.run_sql('data/create_tables.sql', conn)
        
    parser.set_defaults(func=wipe)


def setup_execute_parser(parser):
    """Setup a subparser for the execute subcommand"""

    def execute(args):
        """Execute the statements found in one or more .sql files."""
        if os.path.isdir(args.path):
            paths = filter(
                os.path.isfile, 
                (os.path.join(args.path, f) for f in os.listdir(args.path)))
        else:
            paths = [args.path]

        paths = list(filter(lambda p: p.endswith('.sql'), paths))

        if len(paths) == 0:
            logger.info('No .sql files found at {0}.'.format(args.path))

        db_url = pg_utils.database_url(which='riksdagen')
        with psycopg2.connect(db_url) as conn:
            for path_in in paths:
                logger.info('Executing statements from {0}.'.format(path_in))

                with open(path_in, encoding='utf-8') as f:
                    data_import.execute_statements(data_import.statements(f), conn)
                
                if args.remove:
                    logger.info('Removing {0}.'.format(path_in))
                    os.remove(path_in)

    
    parser.add_argument('path', type=str,
        help='Path to a file or directory of files to execute SQL statements from.')
    parser.add_argument('--remove', '-r', action='store_true',
        help='Remove the source file if successfully executed.')
    parser.set_defaults(func=execute)

if __name__ == '__main__':
    main()