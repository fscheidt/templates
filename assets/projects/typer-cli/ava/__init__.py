from pathlib import Path
import os
import tomllib
from rich.console import Console
from typing import Any, Dict, Tuple, Type
from pydantic.fields import FieldInfo
from pydantic import (
    computed_field,
    Field, 
)
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
    SettingsConfigDict,
)
from dataclasses import dataclass
from loguru import logger

from ava.typer_custom import CustomTyperGroup
from ava.utils import debug_func

console = Console()

# =========================
MAIN_MODULE = "ava"
LOGGER_ENABLE: bool = None
SET_DOT_ENV: bool = None
# =========================

if not LOGGER_ENABLE:
    logger.disable(name=MAIN_MODULE)


class EnvSettings(BaseSettings):
    verbose: str = Field(alias='VERBOSE')
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_nested_delimiter="_",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@dataclass
class CLIContext:
    APP_TOML: Path = None
    APP_ENV_TOML: Path = None
    CONFIG_FILE: str = None
    ENV_FILE: Path = None
    ENV_FILENAME: str = None
    ENV_TEMPLATE: str = None
    MAIN_MODULE: str = None
    PROJECT_NAME: str = None
    PROJECT_ROOT: Path = None
    PROJECT_MODULES: Path = None
    USER_CONFIG_DIR: str = None
    USER_CONFIG_PATH: Path = None
    environment: EnvSettings = None
    search_env: bool = None

    def __post_init__(self):
        assert self.PROJECT_ROOT.exists()
        
        self.PROJECT_MODULES = Path(self.PROJECT_ROOT) / self.PROJECT_NAME
        assert self.PROJECT_MODULES.exists()

        self.APP_TOML = self.PROJECT_MODULES / "settings.toml"
        assert self.APP_TOML.exists()
        self.APP_ENV_TOML = self.PROJECT_MODULES / "settings_env.toml"
        
        self.USER_CONFIG_PATH = Path.home() / self.USER_CONFIG_DIR / self.MAIN_MODULE
        if self.APP_ENV_TOML.exists():
            self.APP_TOML = self.APP_ENV_TOML
        
        self.CONFIG_FILE = f"{str(self.APP_TOML.name)}"
        
        if self.search_env:
            self.ENV_FILE = self.get_or_create_env_file()
            self.environment = EnvSettings(
                _env_file=self.ENV_FILE
            )
    
    def get_or_create_env_file(self) -> Path:

        env_file = Path(self.PROJECT_ROOT) / self.ENV_FILENAME
        if env_file.exists():
            logger.info(f"Found env_file in PROJECT_ROOT: {env_file}")
            logger.info("skipped")
            return env_file
        logger.warning(f"env_file Not Found in PROJECT_ROOT - Searching in $CONFIG_DIR")
        config_dir = self.USER_CONFIG_PATH
        logger.info(f"config_dir exists? {config_dir.exists()} -> {config_dir}")

        # Ensure the directory exists
        config_dir.mkdir(parents=True, exist_ok=True)
        # Define the .env file path
        dotenv_path = config_dir / self.ENV_FILENAME
        
        if dotenv_path.exists():
            logger.debug(f"Found env_file in config_dir: {dotenv_path}")
            return dotenv_path
        # Define the env_example file path
        env_example_path = Path(self.PROJECT_ROOT) / self.ENV_TEMPLATE
        # Write content from env_example to dotenv_path if not already exists
        if not dotenv_path.exists():
            logger.warning(f"env_file Not Found in {dotenv_path} - Generating a new one from template")
            if env_example_path.exists():
                logger.debug(f"Generating env_file from template: {env_example_path}")
                # Copy content from env_example to dotenv_path
                dotenv_content = env_example_path.read_text()
                dotenv_path.write_text(dotenv_content)
                logger.warning("env_file created! Now edit this file and update the variables with your credentials")
                logger.debug(f"{dotenv_path}")
            else:
                raise FileNotFoundError(f"The {env_example_path} file is missing! Unable to create the env file")
        return dotenv_path

    def load_paths(self):
        return {
            'root': f"{self.PROJECT_ROOT}",
            'modules': f"{self.PROJECT_MODULES}",
            'config_path': f"{self.APP_TOML}",
            'config_file': f"{self.CONFIG_FILE}",
            'user_config_path': f"{self.USER_CONFIG_PATH}",
        }

# ============================================================
def create_context(search_env:bool=None) -> CLIContext:
    ctx = CLIContext(
        search_env=search_env,
        PROJECT_NAME = "ava",
        MAIN_MODULE = "ava",
        ENV_FILENAME = ".env",
        ENV_TEMPLATE = "env_example",
        USER_CONFIG_DIR = ".config",
        PROJECT_ROOT = Path(__file__).parent.parent.absolute(),
    )
    os.environ['PROJECT_ROOT'] = str(ctx.PROJECT_ROOT)
    os.environ['PROJECT_MODULES'] = str(ctx.PROJECT_MODULES)
    os.environ['CONFIG_DIR'] = str(ctx.USER_CONFIG_PATH)
    return ctx

context = create_context(search_env=SET_DOT_ENV)

# ============================================================

class TOMLConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings], ) -> None:
        super().__init__(settings_cls)
        self.env_vars = self._load_toml()

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        field_value = self.env_vars.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value
        return d

    def _load_toml(self) -> Dict[str, Any]:
        toml_file = context.APP_TOML
        if not toml_file:
            toml_file = self.config.get("toml_file")
        if not Path(toml_file).exists():
            return {}
        encoding = self.config.get("env_file_encoding")
        return tomllib.loads(Path(toml_file).read_text(encoding=encoding))


# ============================================================
class ResourceItem(BaseSettings):
    path_dir: str | None = None
    model_config = SettingsConfigDict(extra="ignore")

    @computed_field
    @property
    def path(self) -> Path:
        """ expand and resolve the Path with the given env variable """
        return Path(os.path.expandvars(self.path_dir)).expanduser().resolve()


class Resources(BaseSettings):
    data: ResourceItem | None = None
    assigns: ResourceItem | None = None
    model_config = SettingsConfigDict(extra="ignore")


class AppSettings(BaseSettings):
    logger_enabled: bool | None = True
    verbose: bool | None = False
    model_config = SettingsConfigDict(extra="ignore")


class Project(BaseSettings):
    root: Path | None = None
    modules: Path | None = None
    path_settings: Path | None = None
    file_settings: str | None = None
    user_config_path: Path | None = None
    name: str | None = None
    env_file: Path | None = None


class ToolSettings(BaseSettings):
    resources: Resources | None = None
    app: AppSettings | None = None
    _environment: EnvSettings | None = None
    _project: Project | None = None
    _project_paths: dict | None = context.load_paths()

    @staticmethod
    def module_config(modulename: str):
        from importlib import import_module
        from importlib.util import find_spec
        import sys
        modulename = f"{context.MAIN_MODULE}.{modulename}"
        if not find_spec(modulename):
            logger.debug('%s: No such module.' % modulename, file=sys.stderr)
            exit(1)
        module = import_module(modulename)
        module_config = getattr(module, "config")
        return module_config

    @computed_field
    @property
    def environment(self) -> EnvSettings:
        return context.environment 
    
    @computed_field
    @property
    def project(self) -> Project:
        return Project(
            root=self._project_paths['root'],
            modules=self._project_paths['modules'],
            file_settings=self._project_paths['config_file'],
            path_settings=self._project_paths['config_path'],
            user_config_path=self._project_paths['user_config_path'],
            name=context.PROJECT_NAME,
            env_file=context.ENV_FILE
        )
    model_config = SettingsConfigDict(
        env_prefix=f"{context.PROJECT_NAME}_",
        env_nested_delimiter="_",
        env_file_encoding="utf-8",
        extra="ignore",
        toml_file=context.APP_TOML
    )
    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: InitSettingsSource,
            env_settings: EnvSettingsSource,
            dotenv_settings: DotEnvSettingsSource,
            file_secret_settings: SecretsSettingsSource,
    ) -> Tuple[
        InitSettingsSource,
        EnvSettingsSource,
        DotEnvSettingsSource,
        TOMLConfigSettingsSource,
        SecretsSettingsSource,
    ]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TOMLConfigSettingsSource(settings_cls),
            file_secret_settings,
        )
        

# ============================================================
settings = ToolSettings()
