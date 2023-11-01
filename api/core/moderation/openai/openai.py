import openai
import json

from core.helper.encrypter import decrypt_token
from core.moderation.base import Moderation, ModerationException
from extensions.ext_database import db
from models.provider import Provider


class OpenAIModeration(Moderation):
    type = "openai"

    @classmethod
    def validate_config(cls, config: dict):
        cls._validate_inputs_and_outputs_config(config, True)
    
    @classmethod
    def moderation_for_inputs(cls, tenant_id: str, config: dict, inputs: dict, query: str):
        if not config['inputs_configs']['enabled']:
            return
        
        preset_response = config['inputs_configs']['preset_response']
        if query:
            inputs['query__'] = query

        cls._is_violated(tenant_id, inputs, preset_response)

    @classmethod
    def moderation_for_output(cls, tenant_id: str, config: dict, output: str):
        if not config['outputs_configs']['enabled']:
            return

        preset_response = config['inputs_configs']['preset_response']

        cls._is_violated(tenant_id, {"output": output}, preset_response)

    @classmethod
    def _is_violated(cls, tenant_id: str, inputs: dict, preset_response: str):
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        openai_api_key = cls._get_openai_api_key(tenant_id)
        
        moderation_result = openai.Moderation.create(input=list(inputs.values()), api_key=openai_api_key)

        for result in moderation_result.results:
            if result['flagged']:
                raise ModerationException(preset_response)

    @classmethod
    def _get_openai_api_key(cls, tenant_id: str) -> str:
        provider = db.session.query(Provider) \
                    .filter_by(tenant_id=tenant_id) \
                    .filter_by(provider_name="openai") \
                    .first()
        
        if not provider:
            raise ValueError("openai provider is not configured")
        
        encrypted_config = json.loads(provider.encrypted_config)

        return decrypt_token(tenant_id, encrypted_config['openai_api_key'])