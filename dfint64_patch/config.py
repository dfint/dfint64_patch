import functools
from collections.abc import Callable

from loguru import logger
from omegaconf import DictConfig, OmegaConf


def with_config(config_class: type, config_file: str) -> Callable[[Callable[[DictConfig], None]], Callable[[], None]]:
    def decorator(func: Callable[[DictConfig], None]) -> Callable[[], None]:
        @functools.wraps(func)
        def wrapper() -> None:
            config = OmegaConf.structured(config_class)

            config.merge_with(OmegaConf.from_cli())
            try:
                config.merge_with(OmegaConf.load(config_file))
            except FileNotFoundError:
                logger.info(f"Config {config_file} not found, using CLI options only")

            missing = ", ".join(OmegaConf.missing_keys(config))
            if missing:
                logger.error(f"Missing configuration keys: {missing}")
                return
            func(config)

        return wrapper

    return decorator
