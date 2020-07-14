import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from panoramic.auth import OAuth2Client
from panoramic.cli.config.auth import get_client_id, get_client_secret, get_token
from panoramic.cli.config.model import get_base_url

logger = logging.getLogger(__name__)


class ModelClient(OAuth2Client):

    """Model HTTP API client."""

    base_url: str

    def __init__(
        self, base_url: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None,
    ):
        token = get_token()
        base_url = base_url if base_url is not None else get_base_url()
        client_id = client_id if client_id is not None else get_client_id()
        client_secret = client_secret if client_secret is not None else get_client_secret()

        self.base_url = base_url

        if token is not None:
            self.session = requests.Session()
            self.session.headers.update(**{'x-auth-token': token})
        else:
            super().__init__(client_id, client_secret)

    def delete_model(self, data_source: str, company_slug: str, name: str):
        """Delete model with a given name."""
        url = urljoin(self.base_url, name)
        logger.debug(f'Deleting model with name: {name}')
        # TODO: change once company_slug works on API layer
        # params = {'virtual_data_source': data_source, 'company_slug': company_slug}
        params = {'virtual_data_source': 'smoke_test_511_IEGHZ', 'company_id': '41'}
        response = self.session.delete(url, params=params, timeout=5)
        response.raise_for_status()

    def upsert_model(self, data_source: str, company_slug: str, model: Dict[str, Any]):
        """Add or update given model."""
        logger.debug(f'Upserting model with name: {model["name"]}')
        # TODO: change once company_slug works on API layer
        # params = {'virtual_data_source': data_source, 'company_slug': company_slug}
        params = {'virtual_data_source': 'smoke_test_511_IEGHZ', 'company_id': '41'}
        response = self.session.put(self.base_url, params=params, timeout=5)
        response.raise_for_status()

    def get_model_names(self, data_source: str, company_slug: str, offset: int = 0, limit: int = 100) -> List[str]:
        """Retrieve names of all models in a given source."""
        logger.debug(f'Listing names of models for source: {data_source}')
        url = urljoin(self.base_url, 'model-name')
        # TODO: change once company_slug works on API layer
        # params = {'virtual_data_source': data_source, 'company_slug': company_slug, 'offset': offset, 'limit': limit}
        params = {'virtual_data_source': 'smoke_test_511_IEGHZ', 'company_id': '41', 'offset': offset, 'limit': limit}
        response = self.session.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()['data']

    def get_models(
        self, data_source: str, company_slug: str, offset: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve all models in a given source."""
        logger.debug(f'Listing models for source: {data_source}')
        # params = {'virtual_data_source': data_source, 'company_slug': company_slug, 'offset': offset, 'limit': limit}
        params = {'virtual_data_source': 'smoke_test_511_IEGHZ', 'company_id': '41', 'offset': offset, 'limit': limit}
        response = self.session.get(self.base_url, params=params,)
        response.raise_for_status()
        return response.json()['data']