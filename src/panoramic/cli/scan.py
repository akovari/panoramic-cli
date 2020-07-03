import itertools
import logging
import operator

from typing import Dict, Iterable

import requests

from requests.exceptions import RequestException

from panoramic.cli.errors import ScanException, SourceNotFoundException
from panoramic.cli.metadata import MetadataClient
from panoramic.cli.metadata.client import JobState


logger = logging.getLogger(__name__)


class Scanner:

    """Scans metadata for a given source and scope."""

    source_id: str
    client: MetadataClient

    def __init__(self, source_id: str, client: MetadataClient = None):
        self.source_id = source_id

        if client is None:
            self.client = MetadataClient()

    def scan_tables(self, table_filter: str, timeout: int = 60) -> Iterable[Dict]:
        """Scan tables for a given source and filter."""
        logger.debug(f'Starting get tables job with filter {table_filter}')
        try:
            job_id = self.client.create_get_tables_job(self.source_id, table_filter)
            logger.debug(f'Get tables job with id {job_id} started with filter {table_filter}')
        except RequestException as e:
            if e.response and e.response.status == requests.codes.not_found:
                raise SourceNotFoundException(f'Source {self.source_id} not found')
            raise ScanException(f'Error ocurred scanning tables for source {self.source_id}')

        try:
            state = self.client.wait_for_terminal_state(job_id, timeout=timeout)
            if state != JobState.COMPLETED:
                raise ScanException(f'Scan job {job_id} failed')
            yield from self.client.collect_results(job_id)
        except RequestException:
            raise ScanException(f'Error ocurred scanning tables for source {self.source_id}')

    def scan_columns(self, table_filter: str, timeout: int = 60) -> Iterable[Dict]:
        """Scan columns for a given source and filter."""
        logger.debug('Starting get columns job')
        try:
            job_id = self.client.create_get_columns_job(self.source_id, table_filter)
            logger.debug(f'Get columns job with id {job_id} started with filter {table_filter}')
        except requests.HTTPError as e:
            if e.response.status == requests.codes.not_found:
                raise SourceNotFoundException(f'Source {self.source_id} not found')
            raise ScanException(f'Error ocurred scanning columns for source {self.source_id}')

        try:
            state = self.client.wait_for_terminal_state(job_id, timeout=timeout)
            if state != JobState.COMPLETED:
                raise ScanException(f'Scan job {job_id} failed')

            yield from self.client.collect_results(job_id)
        except RequestException:
            raise ScanException(f'Error ocurred scanning columns for source {self.source_id}')
