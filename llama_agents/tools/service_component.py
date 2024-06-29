import json
from typing import Any, Dict, Optional

from llama_index.core.query_pipeline import CustomQueryComponent

from llama_agents.types import ServiceDefinition
from enum import Enum

class ModuleType(str, Enum):
    """Module types.

    NOTE: this is to allow both agent services and component services to be stitched together with
    the pipeline orchestrator.

    Ideally there should not be more types.
    
    """
    AGENT = "agent"
    COMPONENT = "component"


class ServiceComponent(CustomQueryComponent):
    name: str
    description: str

    # Store a set of input keys from upstream modules
    # NOTE: no need to track the output keys, this is a fake module anyways
    input_keys: set

    module_type: ModuleType = ModuleType.AGENT

    def __init__(
        self,
        name: str,
        description: str,
        input_keys: Optional[set] = None,
        module_type: ModuleType = ModuleType.AGENT,
    ) -> None:
        self.name = name
        self.description = description
        
        self.input_keys = input_keys or {"input"}

        self.module_type = module_type

    @classmethod
    def from_service_definition(
        cls, 
        service_def: ServiceDefinition,
        input_keys: Optional[set] = None,
        module_type: ModuleType = ModuleType.AGENT,
    ) -> "ServiceComponent":
        return cls(
            name=service_def.service_name, 
            description=service_def.description,
            input_keys=input_keys,
            module_type=module_type,
        )

    @classmethod
    def from_component_service(
        cls,
        component_service: Any,
    ) -> "ServiceComponent":
        """Create a service component from a component service."""
        from llama_agents.services.component import ComponentService

        if not isinstance(component_service, ComponentService):
            raise ValueError("component_service must be a Component")
        
        component = component_service.component
        return cls.from_service_definition(
            component_service.service_definition,
            input_keys=component.input_keys,
            module_type=ModuleType.COMPONENT
        )

    @property
    def _input_keys(self) -> set:
        """Input keys dict."""
        return self.input_keys

    @property
    def _output_keys(self) -> set:
        return {"service_output"}

    def _run_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Return a dummy output."""
        json_dump = json.dumps(
            {
                "name": self.name,
                "description": self.description,
                "input": kwargs,
            }
        )
        return {"service_output": json_dump}

    async def _arun_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Return a dummy output."""
        json_dump = json.dumps(
            {
                "name": self.name,
                "description": self.description,
                "input": kwargs,
            }
        )
        return {"service_output": json_dump}
