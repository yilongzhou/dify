import importlib
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict

import yaml

from core.model_runtime.entities.model_entities import ModelType, AIModelEntity
from core.model_runtime.entities.provider_entities import ProviderEntity
from core.model_runtime.model_providers.__base.ai_model import AIModel


class ModelProvider(ABC):
    provider_schema: ProviderEntity = None
    model_class_map: Dict[str, type[AIModel]] = {}

    @abstractmethod
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials
        You can choose any validate_credentials method of model type or implement validate method by yourself,
        such as: get model list api

        if validate failed, raise exception

        :param credentials: provider credentials, credentials form defined in `provider_credential_schema`.
        """
        raise NotImplementedError

    def get_provider_schema(self) -> ProviderEntity:
        """
        Get provider schema

        :return: provider schema
        """
        if self.provider_schema:
            return self.provider_schema

        # get dirname of the current path
        provider_name = self.__class__.__module__.split('.')[-1]

        # get the path of the model_provider classes
        base_path = os.path.abspath(__file__)
        current_path = os.path.join(os.path.dirname(os.path.dirname(base_path)), provider_name)

        # read provider schema from yaml file
        yaml_path = os.path.join(current_path, f'{provider_name}.yaml')
        yaml_data = {}
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                yaml_data = yaml.safe_load(f)

        # yaml_data to entity
        provider_schema = ProviderEntity(**yaml_data)

        # cache schema
        self.provider_schema = provider_schema

        return provider_schema

    def models(self, model_type: ModelType, remote_model_fetch_credentials: Optional[dict] = None) -> list[AIModelEntity]:
        """
        Get all models for given model type

        :param model_type: model type defined in `ModelType`
        :param remote_model_fetch_credentials: credentials for fetching remote models if you want to fetch remote models
        :return: list of models
        """
        # get model instance of the model type
        model_instance = self.get_model_instance(model_type)

        # get predefined models (predefined_models)
        models = model_instance.predefined_models()

        # continue to get remote models if remote_model_fetch_credentials is provided
        if remote_model_fetch_credentials:
            # get remote models from remote api
            remote_models = model_instance.remote_models(remote_model_fetch_credentials)

            if remote_models:
                # merge predefined_models and remote_models
                predefined_model_ids = [model.model for model in models]
                for remote_model in remote_models:
                    if remote_model.model not in predefined_model_ids:
                        models.append(remote_model)

        # return models
        return models

    def get_model_instance(self, model_type: ModelType) -> AIModel:
        """
        Get model instance

        :param model_type: model type defined in `ModelType`
        :return:
        """
        # get dirname of the current path
        provider_name = self.__class__.__module__.split('.')[-1]

        if model_type in self.model_class_map:
            return self.model_class_map[f"{provider_name}.{model_type.value}"]()

        # get the path of the model type classes
        base_path = os.path.abspath(__file__)
        model_type_name = model_type.value.replace('-', '_')
        model_type_path = os.path.join(os.path.dirname(os.path.dirname(base_path)), provider_name, model_type_name)
        model_type_py_path = os.path.join(model_type_path, f'{model_type_name}.py')

        if not os.path.isdir(model_type_path) or not os.path.exists(model_type_py_path):
            raise Exception(f'Invalid model type {model_type} for provider {provider_name}')

        # Dynamic loading {model_type_name}.py file and find the subclass of AIModel
        parent_module = '.'.join(self.__class__.__module__.split('.')[:-1])
        spec = importlib.util.spec_from_file_location(f"{parent_module}.{model_type_name}.{model_type_name}", model_type_py_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        model_class = None
        for name, obj in vars(mod).items():
            if (isinstance(obj, type) and issubclass(obj, AIModel) and not obj.__abstractmethods__
                    and obj != AIModel):
                model_class = obj
                break

        if not model_class:
            raise Exception(f'Missing AIModel Class for model type {model_type} in {model_type_py_path}')

        self.model_class_map[f"{provider_name}.{model_type.value}"] = model_class

        return model_class()