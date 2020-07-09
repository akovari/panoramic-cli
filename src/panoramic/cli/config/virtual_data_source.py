import os

BASE_URL = 'https://diesel.panoramicprod.com/api/v1/federated/virtual-data-source/'


def get_base_url() -> str:
    return os.environ.get('PANO_METADATA_BASE_URL', BASE_URL)
