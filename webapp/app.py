import logging

from apps.api.views import blueprint as api_bp
from apps.main.views import blueprint as main_bp
from db.models import Document
from elasticsearch import AsyncElasticsearch
from environs import Env
from init_scripts import run_init_check
from quart import Quart
from quart_schema import QuartSchema
from tortoise import Tortoise

env = Env()
env.read_env()
es = None


def create_app():
    app = Quart(
        __name__,
        template_folder="./_templates",
        static_folder="_static",
        static_url_path="/static",
    )
    app.config.from_prefixed_env("APP")
    app.config["DEBUG"] = env.bool("APP_DEBUG")
    app.store = {"es": None}

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    QuartSchema(app)

    if app.config["DEBUG"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    return app


app = create_app()


@app.after_serving
async def app_shutdown():
    await Tortoise.close_connections()
    await es.close()


@app.before_serving
async def app_start():
    global es
    app.logger.debug(app.config)
    if app.config["DB"] == "SQLITE":
        app.logger.debug("=== Choosed SQLITE")
        db_url = f"sqlite://{app.config['SQLITE_PATH']}"
    elif app.config["DB"] == "PG":
        app.logger.debug("=== Choosed PG")
        db_url = "postgres://{}:{}@{}:{}/{}".format(
            app.config["PG_USERNAME"],
            app.config["PG_PASS"],
            app.config["PG_HOST"],
            app.config["PG_PORT"],
            app.config["PG_DB_NAME"],
        )
    else:
        raise ValueError("Please provide correct db type in ENV")

    app.store["es"] = AsyncElasticsearch(
        f"http://{app.config['ES_HOST']}:{app.config['ES_PORT']}"
    )
    await Tortoise.init(db_url=db_url, modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()

    if app.config["INIT_CONTENT_CHECK"] == "True":
        app.logger.debug("=== Init Content Check")
        await run_init_check(
            Document, es=app.store["es"], es_index=app.config["ES_INDEX"]
        )


if __name__ == "__main__":
    app.run()
