from core.moderation.base import Moderation


class ApiBasedModeration(Moderation):
    type = "api_based"

    @classmethod
    def validate_config(cls, config: dict) -> None:
        api_based_extension_id = config.get("api_based_extension_id")
        if not api_based_extension_id:
            raise ValueError("api_based_extension_id is required")
        
        cls._validate_inputs_and_outputs_config(config, False)

    @classmethod
    def moderation_for_inputs(cls, tenant_id: str, config: dict, inputs: dict, query: str):
        pass

    @classmethod
    def moderation_for_output(cls, tenant_id: str, config: dict, output: str):
        pass