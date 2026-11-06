from typing import Type, Optional
from engine.core.base import BaseGenerator, BaseValidator


class AgentRegistry:
    """Central registry mapping skill names to their Generator and Validator classes."""

    _registry: dict[str, tuple[Type[BaseGenerator], Type[BaseValidator]]] = {}

    @classmethod
    def register(cls, skill_name: str, generator_cls: Type[BaseGenerator], validator_cls: Type[BaseValidator]) -> None:
        cls._registry[skill_name] = (generator_cls, validator_cls)

    @classmethod
    def get_agents(cls, skill_name: str) -> tuple[BaseGenerator, BaseValidator]:
        if skill_name not in cls._registry:
            raise KeyError(f"Skill '{skill_name}' is not registered in AgentRegistry. Available: {cls.list_skills()}")
        gen_cls, val_cls = cls._registry[skill_name]
        return gen_cls(name=f"{skill_name}_generator", skill_name=skill_name, role="Generator"), val_cls(
            name=f"{skill_name}_validator", skill_name=skill_name, role="Validator"
        )

    @classmethod
    def list_skills(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()
