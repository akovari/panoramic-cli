import logging
import sys
from typing import Optional

import click
import yaml
from dotenv import load_dotenv

from panoramic.cli.__version__ import __version__
from panoramic.cli.companies.client import CompaniesClient
from panoramic.cli.context import ContextAwareCommand
from panoramic.cli.local.file_utils import Paths
from panoramic.cli.logging import echo_error, log_error


@click.group(context_settings={'help_option_names': ["-h", "--help"]})
@click.option('--debug', is_flag=True, help='Enables debug mode')
@click.version_option(__version__)
def cli(debug):
    if debug:
        logger = logging.getLogger()
        logger.setLevel("DEBUG")

    load_dotenv(dotenv_path=Paths.dotenv_file())

    from panoramic.cli.supported_version import is_version_supported

    if not is_version_supported(__version__):
        exit(1)


@cli.command(help='Scan models from source', cls=ContextAwareCommand)
@click.argument('source-id', type=str, required=True)
@click.option('--filter', '-f', type=str, help='Filter down what schemas to scan')
@click.option('--parallel', '-p', type=int, default=8, help='Parallelize metadata scan')
def scan(source_id: str, filter: Optional[str], parallel: int):
    from panoramic.cli.command import scan as scan_command

    try:
        scan_command(source_id, filter, parallel)
    except Exception:
        echo_error('Internal error occurred', exc_info=True)
        sys.exit(1)


@cli.command(help='Pull models from remote', cls=ContextAwareCommand)
def pull():
    from panoramic.cli.command import pull

    try:
        pull()
    except Exception:
        echo_error('Internal error occurred', exc_info=True)
        sys.exit(1)


@cli.command(help='Push models to remote', cls=ContextAwareCommand)
def push():
    from panoramic.cli.command import push

    try:
        push()
    except Exception:
        echo_error('Internal error occurred', exc_info=True)
        sys.exit(1)


@cli.command(help='Configure pano CLI options')
def configure():
    client_id = click.prompt('Enter your client id', type=str)
    client_secret = click.prompt('Enter your client secret', hide_input=True, type=str)

    config_file = Paths.config_file()
    if not config_file.parent.exists():
        config_file.parent.mkdir()

    with open(config_file, 'w+') as f:
        f.write(yaml.safe_dump({'client_id': client_id, 'client_secret': client_secret}))


@cli.command(help='Initialize metadata repository')
def init():
    # TODO: move to command
    logger = logging.getLogger(__name__)

    client = CompaniesClient()

    try:
        companies = client.get_companies()
    except Exception as error:
        log_error(logger, 'Failed to fetch available companies', error)
        companies = []

    base_text = 'Enter your company slug'
    if len(companies) == 0:
        prompt_text = base_text
    elif len(companies) > 3:
        prompt_text = f'{base_text} (Available - {{{",".join(companies)}}},...)'
    else:
        prompt_text = f'{base_text} (Available - {{{",".join(companies)}}})'

    company_slug = click.prompt(prompt_text, type=str, default=next(iter(companies), None))

    context_file = Paths.context_file()
    with open(context_file, 'w') as f:
        f.write(yaml.safe_dump({'company_slug': company_slug, 'api_version': 'v1'}))


@cli.command(help='List available data connections', cls=ContextAwareCommand)
def list_connections():
    from panoramic.cli.command import list_connections

    try:
        list_connections()
    except Exception:
        echo_error('Internal error occurred', exc_info=True)
        sys.exit(1)


@cli.command(help='List available data connections')
def list_companies():
    try:
        list_companies()
    except Exception:
        echo_error('Internal error occurred', exc_info=True)
        sys.exit(1)
