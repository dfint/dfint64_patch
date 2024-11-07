import functools
from collections.abc import Callable
from typing import TypeVar

from loguru import logger
from omegaconf import DictConfig, OmegaConf

T = TypeVar("T", bound=DictConfig)


def with_config(config_class: type, *config_files: str) -> Callable[[Callable[[T], None]], Callable[[], None]]:
    """
    A decorator to load the config file and merge it with the CLI options.
    """

    def decorator(func: Callable[[T], None]) -> Callable[[], None]:
        @functools.wraps(func)
        def wrapper() -> None:
            config = OmegaConf.structured(config_class)

            config.merge_with(OmegaConf.from_cli())

            for config_file in config_files:
                try:
                    config.merge_with(OmegaConf.load(config_file))
                except FileNotFoundError:  # noqa: PERF203
                    logger.info(f"Config {config_file} not found, using CLI options only")

            missing = ", ".join(OmegaConf.missing_keys(config))
            if missing:
                logger.error(f"Missing configuration keys: {missing}")
                return
            func(config)

        return wrapper

    return decorator
