# Unzip the dependencies managed by serverless-python-requirements
try:
    import unzip_requirements  # type:ignore
except ImportError:
    pass

#
# Imports
#

import json
import logging
import os

import boto3
import openai
from slack_bolt import Ack, App, BoltContext
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.aws_lambda.lambda_s3_oauth_flow import LambdaS3OAuthFlow
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
from slack_sdk.web import WebClient

from app.bolt_listeners import before_authorize, register_listeners
from app.config import Config
from app.i18n import translate
from app.slack_ops import DEFAULT_HOME_TAB_MESSAGE, build_home_tab

#
# Product deployment (AWS Lambda)
#
# export SLACK_CLIENT_ID=
# export SLACK_CLIENT_SECRET=
# export SLACK_SIGNING_SECRET=
# export SLACK_SCOPES=app_mentions:read,channels:history,groups:history,im:history,mpim:history,chat:write.public,chat:write,users:read
# export SLACK_INSTALLATION_S3_BUCKET_NAME=
# export SLACK_STATE_S3_BUCKET_NAME=
# export OPENAI_S3_BUCKET_NAME=
# npm install -g serverless
# serverless plugin install -n serverless-python-requirements
# serverless deploy
#


SlackRequestHandler.clear_all_log_handlers()
logging.basicConfig(format="%(asctime)s %(message)s", level=Config.SLACK_APP_LOG_LEVEL)

s3_client = boto3.client("s3")
openai_bucket_name = os.environ["OPENAI_S3_BUCKET_NAME"]

client_template = WebClient()
client_template.retry_handlers.append(RateLimitErrorRetryHandler(max_retry_count=2))


def register_revocation_handlers(app: App):
    # Handle uninstall events and token revocations
    @app.event("tokens_revoked")
    def handle_tokens_revoked_events(
        event: dict,
        context: BoltContext,
        logger: logging.Logger,
    ):
        user_ids = event.get("tokens", {}).get("oauth", [])
        if len(user_ids) > 0:
            for user_id in user_ids:
                app.installation_store.delete_installation(
                    enterprise_id=context.enterprise_id,
                    team_id=context.team_id,
                    user_id=user_id,
                )
        bots = event.get("tokens", {}).get("bot", [])
        if len(bots) > 0:
            app.installation_store.delete_bot(
                enterprise_id=context.enterprise_id,
                team_id=context.team_id,
            )
            try:
                s3_client.delete_object(Bucket=openai_bucket_name, Key=context.team_id)
            except Exception as e:
                logger.error(
                    f"Failed to delete an OpenAI auth key: (team_id: {context.team_id}, error: {e})"
                )

    @app.event("app_uninstalled")
    def handle_app_uninstalled_events(
        context: BoltContext,
        logger: logging.Logger,
    ):
        app.installation_store.delete_all(
            enterprise_id=context.enterprise_id,
            team_id=context.team_id,
        )
        try:
            s3_client.delete_object(Bucket=openai_bucket_name, Key=context.team_id)
        except Exception as e:
            logger.error(
                f"Failed to delete an OpenAI auth key: (team_id: {context.team_id}, error: {e})"
            )


def handler(event, context_):
    app = App(
        process_before_response=True,
        before_authorize=before_authorize,
        oauth_flow=LambdaS3OAuthFlow(),
        client=client_template,
    )
    app.oauth_flow.settings.install_page_rendering_enabled = False
    register_listeners(app)
    register_revocation_handlers(app)

    if Config.USE_SLACK_LANGUAGE is True:

        @app.middleware
        def set_locale(
            context: BoltContext,
            client: WebClient,
            logger: logging.Logger,
            next_,
        ):
            bot_scopes = context.authorize_result.bot_scopes
            if bot_scopes is not None and "users:read" in bot_scopes:
                user_id = context.actor_user_id or context.user_id
                try:
                    user_info = client.users_info(user=user_id, include_locale=True)
                    context["locale"] = user_info.get("user", {}).get("locale")
                except SlackApiError as e:
                    logger.debug(f"Failed to fetch user info due to {e}")
                    pass
            next_()

    @app.middleware
    def set_s3_openai_api_key(context: BoltContext, next_):
        try:
            s3_response = s3_client.get_object(
                Bucket=openai_bucket_name, Key=context.team_id
            )
            config_str: str = s3_response["Body"].read().decode("utf-8")
            if config_str.startswith("{"):
                config = json.loads(config_str)
                context["OPENAI_API_KEY"] = config.get("api_key")
                context["OPENAI_MODEL"] = config.get("model")
                context["OPENAI_TEMPERATURE"] = config.get(
                    "temperature", Config.OPENAI_TEMPERATURE
                )
            else:
                # The legacy data format
                context["OPENAI_API_KEY"] = config_str
                context["OPENAI_MODEL"] = Config.OPENAI_MODEL
                context["OPENAI_TEMPERATURE"] = Config.OPENAI_TEMPERATURE
        except:  # noqa: E722
            context["OPENAI_API_KEY"] = None
            context["OPENAI_MODEL"] = None
            context["OPENAI_TEMPERATURE"] = None

        context["OPENAI_API_TYPE"] = Config.OPENAI_API_TYPE
        context["OPENAI_API_BASE"] = Config.OPENAI_API_BASE
        context["OPENAI_API_VERSION"] = Config.OPENAI_API_VERSION
        context["OPENAI_DEPLOYMENT_ID"] = Config.OPENAI_DEPLOYMENT_ID
        context[
            "OPENAI_FUNCTION_CALL_MODULE_NAME"
        ] = Config.OPENAI_FUNCTION_CALL_MODULE_NAME
        next_()

    @app.event("app_home_opened")
    def render_home_tab(client: WebClient, context: BoltContext):
        message = DEFAULT_HOME_TAB_MESSAGE
        try:
            s3_client.get_object(Bucket=openai_bucket_name, Key=context.team_id)
            message = "This app is ready to use in this workspace :raised_hands:"
        except:  # noqa: E722
            pass
        openai_api_key = context.get("OPENAI_API_KEY")
        client.views_publish(
            user_id=context.user_id,
            view=build_home_tab(
                openai_api_key=openai_api_key,
                context=context,
                message=message,
            ),
        )

    @app.action("configure")
    def handle_some_action(ack, body: dict, client: WebClient, context: BoltContext):
        ack()
        already_set_api_key = context.get("OPENAI_API_KEY")
        api_key_text = "Save your OpenAI API key:"
        submit = "Submit"
        cancel = "Cancel"
        if already_set_api_key is not None:
            api_key_text = translate(
                openai_api_key=already_set_api_key, context=context, text=api_key_text
            )
            submit = translate(
                openai_api_key=already_set_api_key, context=context, text=submit
            )
            cancel = translate(
                openai_api_key=already_set_api_key, context=context, text=cancel
            )

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "configure",
                "title": {"type": "plain_text", "text": "OpenAI API Key"},
                "submit": {"type": "plain_text", "text": submit},
                "close": {"type": "plain_text", "text": cancel},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "api_key",
                        "label": {"type": "plain_text", "text": api_key_text},
                        "element": {"type": "plain_text_input", "action_id": "input"},
                    },
                    {
                        "type": "input",
                        "block_id": "model",
                        "label": {"type": "plain_text", "text": "OpenAI Model"},
                        "element": {
                            "type": "static_select",
                            "action_id": "input",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "GPT-3.5 Turbo",
                                    },
                                    "value": "gpt-3.5-turbo",
                                },
                                {
                                    "text": {"type": "plain_text", "text": "GPT-4 8K"},
                                    "value": "gpt-4",
                                },
                                {
                                    "text": {"type": "plain_text", "text": "GPT-4 32K"},
                                    "value": "gpt-4-32k",
                                },
                            ],
                            "initial_option": {
                                "text": {
                                    "type": "plain_text",
                                    "text": "GPT-3.5 Turbo",
                                },
                                "value": "gpt-3.5-turbo",
                            },
                        },
                    },
                ],
            },
        )

    def validate_api_key_registration(ack: Ack, view: dict, context: BoltContext):
        already_set_api_key = context.get("OPENAI_API_KEY")

        inputs = view["state"]["values"]
        api_key = inputs["api_key"]["input"]["value"]
        model = inputs["model"]["input"]["selected_option"]["value"]
        try:
            # Verify if the API key is valid
            openai.Model.retrieve(api_key=api_key, id="gpt-3.5-turbo")
            try:
                # Verify if the given model works with the API key
                openai.Model.retrieve(api_key=api_key, id=model)
            except Exception:
                text = "This model is not yet available for this API key"
                if already_set_api_key is not None:
                    text = translate(
                        openai_api_key=already_set_api_key, context=context, text=text
                    )
                ack(
                    response_action="errors",
                    errors={"model": text},
                )
                return
            ack()
        except Exception:
            text = "This API key seems to be invalid"
            if already_set_api_key is not None:
                text = translate(
                    openai_api_key=already_set_api_key, context=context, text=text
                )
            ack(
                response_action="errors",
                errors={"api_key": text},
            )

    def save_api_key_registration(
        view: dict,
        logger: logging.Logger,
        context: BoltContext,
    ):
        inputs = view["state"]["values"]
        api_key = inputs["api_key"]["input"]["value"]
        model = inputs["model"]["input"]["selected_option"]["value"]
        try:
            openai.Model.retrieve(api_key=api_key, id=model)
            s3_client.put_object(
                Bucket=openai_bucket_name,
                Key=context.team_id,
                Body=json.dumps({"api_key": api_key, "model": model}),
            )
        except Exception as e:
            logger.exception(e)

    app.view("configure")(
        ack=validate_api_key_registration,
        lazy=[save_api_key_registration],
    )

    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context_)
