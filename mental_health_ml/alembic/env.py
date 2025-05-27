# # alembic/env.py

# import os
# import sys
# from logging.config import fileConfig

# from sqlalchemy import engine_from_config
# from sqlalchemy import pool

# from alembic import context

# # --- CUSTOM SETUP START ---
# # 1. Ensure the project's root directory is in the Python path
# # This allows Alembic to import modules from your 'mental_health_ml' package
# # The path '..' assumes 'alembic' directory is directly inside 'mental_health_ml'
# app_root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# sys.path.insert(0, app_root_directory)
# print(f"Added to sys.path: {app_root_directory}") # For debugging

# # 2. Load environment variables from .env file located in the app_root_directory
# from dotenv import load_dotenv
# dotenv_path = os.path.join(app_root_directory, '.env') # Looks for G:\mhd-app\.env
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)
#     print(f"Successfully loaded .env file from: {dotenv_path}") # For debugging
#     # For debugging, print the DATABASE_URL to confirm it's loaded
#     # print(f"DATABASE_URL from .env: {os.getenv('DATABASE_URL')}")
# else:
#     print(f"Warning: .env file not found at {dotenv_path}. DATABASE_URL might not be set.")


# # 3. Import your SQLAlchemy Base and all your models
# try:
#     from mental_health_ml.config.db import Base
#     from mental_health_ml.models import db_models # Ensure all models are imported here or in db_models.__init__
#     print("Successfully imported Base and db_models.") # For debugging
# except ImportError as e:
#     print(f"Error importing Base or models: {e}")
#     print("Ensure 'mental_health_ml.config.db.Base' and 'mental_health_ml.models.db_models' are correct.")
#     print(f"Current sys.path: {sys.path}")
#     sys.exit(1)
# except ModuleNotFoundError as e: # More specific catch
#     print(f"ModuleNotFoundError importing Base or models: {e}")
#     print(f"Current sys.path: {sys.path}")
#     sys.exit(1)

# # 4. Set target_metadata for Alembic
# # This tells Alembic what the "target" schema (defined by your models) is.
# target_metadata = Base.metadata
# # --- CUSTOM SETUP END ---

# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config

# # Interpret the config file for Python logging.
# # This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)


# # other values from the config, defined by the needs of env.py,
# # can be acquired:
# # my_important_option = config.get_main_option("my_important_option")
# # ... etc.

# # Add this function somewhere before run_migrations_online/offline
# def include_object(object, name, type_, reflected, compare_to):
#     """
#     Should you include this table or sequence in the autogenerate pass?
#     Return True to include, False to exclude.
#     """
#     if type_ == "table" and (
#         name.startswith("mlflow_") or  # Standard MLflow prefix if using newer MLflow
#         name in ["experiments", "runs", "metrics", "params", "tags",
#                  "registered_models", "model_versions", "latest_metrics",
#                  "model_version_tags", "registered_model_tags", "experiment_tags",
#                  "model_versions_artifacts", "datasets", "input_tags", "inputs"] # Add other known MLflow table names
#     ):
#         return False  # Exclude MLflow tables
#     else:
#         return True # Include all other tables (your application tables)

# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""
#     # ... (your existing code to get connectable) ...
#     connectable = ... # your engine_from_config or create_engine call

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection,
#             target_metadata=target_metadata,
#             include_object=include_object,  # <<<<<< ADD THIS
#             compare_type=True # Optional: helps compare column types more accurately
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode.

#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.

#     Calls to context.execute() here emit the given string to the
#     script output.

#     """
#     # --- CUSTOM CHANGE FOR OFFLINE MODE ---
#     # Ensure DATABASE_URL from .env is used if alembic.ini refers to it.
#     # If config.get_main_option("sqlalchemy.url") already has the resolved URL, this is fine.
#     # If it's still "${DATABASE_URL}", we need to provide the actual URL.
#     db_url = os.getenv("DATABASE_URL")
#     if not db_url:
#         # Fallback to alembic.ini if DATABASE_URL is not in env for some reason
#         db_url = config.get_main_option("sqlalchemy.url")
#         if not db_url or "${DATABASE_URL}" in db_url: # Check if it's still a placeholder
#              raise ValueError(
#                 "DATABASE_URL not set in environment and not properly "
#                 "configured in alembic.ini for offline mode."
#             )
#     context.configure(
#         url=db_url, # Use the resolved database URL
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )
#     # --- END CUSTOM CHANGE FOR OFFLINE MODE ---

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.

#     In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """
#     # --- CUSTOM CHANGE FOR ONLINE MODE ---
#     # section will be the [alembic] section from alembic.ini
#     ini_section = config.get_section(config.config_ini_section, {})

#     # Override sqlalchemy.url from alembic.ini with the one from .env if necessary,
#     # especially if the .ini file uses ${DATABASE_URL} placeholder.
#     db_url_from_env = os.getenv("DATABASE_URL")
#     if db_url_from_env:
#         ini_section['sqlalchemy.url'] = db_url_from_env
#         print(f"Using DATABASE_URL from environment for Alembic: {db_url_from_env}") # For debugging
#     elif "${DATABASE_URL}" in ini_section.get('sqlalchemy.url', ''):
#         print("Error: DATABASE_URL placeholder found in alembic.ini but DATABASE_URL environment variable is not set.")
#         raise ValueError(
#             "DATABASE_URL placeholder found in alembic.ini but "
#             "DATABASE_URL environment variable is not set."
#         )
#     else: # If no placeholder and no env var, use what's in ini (could be hardcoded)
#         print(f"Using sqlalchemy.url directly from alembic.ini: {ini_section.get('sqlalchemy.url')}") # Debug

#     connectable = engine_from_config(
#         ini_section, # Use the potentially updated ini_section
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )
#     # --- END CUSTOM CHANGE FOR ONLINE MODE ---

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()

# alembic/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- CUSTOM SETUP START ---
# 1. Ensure the project's root directory is in the Python path
app_root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, app_root_directory)
print(f"Added to sys.path: {app_root_directory}")

# 2. Load environment variables from .env file
from dotenv import load_dotenv
dotenv_path = os.path.join(app_root_directory, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Successfully loaded .env file from: {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}. DATABASE_URL might not be set.")

# 3. Import your SQLAlchemy Base and all your models
try:
    from mental_health_ml.config.db import Base
    # Ensure mental_health_ml.models.db_models imports/defines ALL your application's tables
    from mental_health_ml.models import db_models
    print("Successfully imported Base and db_models.")
except ImportError as e:
    print(f"Error importing Base or models: {e}")
    print("Ensure 'mental_health_ml.config.db.Base' and 'mental_health_ml.models.db_models' are correct.")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError importing Base or models: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# 4. Set target_metadata for Alembic
target_metadata = Base.metadata

# 5. Define function to control object inclusion for autogenerate
#    and list of tables to ignore (e.g., MLflow tables)
TABLES_TO_IGNORE = [
    # Common MLflow table names (adjust if your MLflow version uses different ones)
    "experiments", "runs", "metrics", "params", "tags", "latest_metrics",
    "registered_models", "model_versions",
    "model_version_tags", "registered_model_tags", "experiment_tags",
    "registered_model_aliases",
        # MLflow Tracking V2 / Tracing / Datasets tables
    "inputs", "input_tags",              # <--- ADDED
    "datasets",                          # <--- ADDED
    "trace_info", "trace_tags", 
    "trace_request_metadata", 
    # Older MLflow might have "latest_versions"
    "users_backup",  
    # If MLflow uses a prefix like "mlflow_", you could use name.startswith("mlflow_")
    # Add other tables managed by external tools if necessary
]

def include_object(object, name, type_, reflected, compare_to):
    """
    Determines if an object should be included in the autogenerate diff.
    """
    if type_ == "table":
        # Check if the table name is in our explicit ignore list
        if name in TABLES_TO_IGNORE:
            return False
        # Example for ignoring tables with a specific prefix (if applicable)
        # if name.startswith("mlflow_"):
        #     return False
    # Default: include all other objects (columns, indexes, sequences, etc.)
    # and tables not in the ignore list.
    return True
# --- CUSTOM SETUP END ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url_from_ini = config.get_main_option("sqlalchemy.url")
        if not db_url_from_ini or "${DATABASE_URL}" in db_url_from_ini:
            raise ValueError(
                "DATABASE_URL not set in environment and not properly "
                "configured in alembic.ini (or is still a placeholder)."
            )
        db_url = db_url_from_ini
    
    print(f"Offline mode using DB URL: {db_url}") # For debugging

    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,      # <--- MODIFIED HERE
        compare_type=True                   # <--- ADDED/MODIFIED HERE
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    ini_section = config.get_section(config.config_ini_section, {})

    db_url_from_env = os.getenv("DATABASE_URL")
    if db_url_from_env:
        ini_section['sqlalchemy.url'] = db_url_from_env
        print(f"Online mode: Using DATABASE_URL from environment for Alembic: {db_url_from_env}")
    elif ini_section.get('sqlalchemy.url') and "${DATABASE_URL}" in ini_section['sqlalchemy.url']:
        print("Error: DATABASE_URL placeholder found in alembic.ini but DATABASE_URL environment variable is not set.")
        raise ValueError(
            "DATABASE_URL placeholder found in alembic.ini but "
            "DATABASE_URL environment variable is not set."
        )
    else:
        print(f"Online mode: Using sqlalchemy.url directly from alembic.ini: {ini_section.get('sqlalchemy.url')}")

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,      # <--- MODIFIED HERE
            compare_type=True                   # <--- ADDED/MODIFIED HERE
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    print("Running migrations in offline mode...")
    run_migrations_offline()
else:
    print("Running migrations in online mode...")
    run_migrations_online()