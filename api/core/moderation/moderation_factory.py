from core.moderation.base import Moderation
from core.extension.extensible import ExtensionModule
from extensions.ext_code_based_extension import code_based_extension


class ModerationFactory:
    __moderation_class: Moderation

    def __init__(self, name: str):
        self.__moderation_class = code_based_extension.extension_class(ExtensionModule.MODERATION, name)

    def validate_config(self, config: dict) -> None:
        self.__moderation_class.validate_config(config)

    def moderation_for_inputs(self, tenant_id: str, config: dict, inputs: dict, query: str):
        self.__moderation_class.moderation_for_inputs(tenant_id, config, inputs, query)

    def moderation_for_output(self, tenant_id: str, config: dict, output: str):
        self.__moderation_class.moderation_for_output(tenant_id, config, output)
