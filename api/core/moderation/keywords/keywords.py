from core.moderation.base import Moderation, ModerationException

class KeywordsModeration(Moderation):
    type = "keywords"

    @classmethod
    def validate_config(cls, config):
        if not config.get("keywords"):
            raise ValueError("keywords is required")
        cls._validate_inputs_and_outputs_config(config, True)

    @staticmethod
    def _check_keywords_in_text(keywords_list, text):
        for keyword in keywords_list:
            if keyword in text:
                return True
        return False
    
    @classmethod
    def moderation_for_inputs(cls, tenant_id: str, config: dict, inputs: dict, query: str):
        if not config['inputs_configs']['enabled']:
            return
        
        keywords_list = config['keywords'].split('\n')
        preset_response = config['inputs_configs']['preset_response']

        for value in inputs.values():
            if cls._check_keywords_in_text(keywords_list, value):
                raise ModerationException(preset_response)

        if cls._check_keywords_in_text(keywords_list, query):
            raise ModerationException(preset_response)

    @classmethod
    def moderation_for_output(cls, tenant_id: str, config: dict, output: str):
        if not config['outputs_configs']['enabled']:
            return

        keywords_list = config['keywords'].split('\n')
        preset_response = config['outputs_configs']['preset_response']

        if cls._check_keywords_in_text(keywords_list, output):
            raise ModerationException(preset_response)