from .utils import load_config, succeeds, fails, requires_root

from fabric.api import env
env.base_service_directory = '/srv'

__all__ = ['load_config', 'succeeds', 'fails', 'requires_root']
