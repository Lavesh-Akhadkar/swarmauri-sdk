from typing import Any, Callable, Dict, List, Optional
from pydantic import Field, ConfigDict
import re
from swarmauri.stanard.chains.concrete.ChainStep import ChainStep
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.chains.IChainContext import IChainContext


class ChainContextBase(IChainContext, ComponentBase):
    steps: List[ChainStep] = []
    context: Dict = {}
    resource: Optional[str] =  Field(default=ResourceTypes.CHAIN.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)

    def update(self, **kwargs):
        self.context.update(kwargs)

    def get_value(self, key: str) -> Any:
        return self.context.get(key)

    def _resolve_fstring(self, template: str) -> str:
        pattern = re.compile(r'{([^}]+)}')
        def replacer(match):
            expression = match.group(1)
            try:
                return str(eval(expression, {}, self.context))
            except Exception as e:
                print(f"Failed to resolve expression: {expression}. Error: {e}")
                return f"{{{expression}}}"
        return pattern.sub(replacer, template)

    def _resolve_placeholders(self, value: Any) -> Any:
        if isinstance(value, str):
            return self._resolve_fstring(value)
        elif isinstance(value, dict):
            return {k: self._resolve_placeholders(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._resolve_placeholders(v) for v in value]
        else:
            return value

    def _resolve_ref(self, value: Any) -> Any:
        if isinstance(value, str) and value.startswith('$'):
            placeholder = value[1:]
            return placeholder
        return value