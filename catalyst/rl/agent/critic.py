from typing import Dict, Tuple  # isort:skip
import copy

from gym import spaces

from catalyst.rl.core import CriticSpec, EnvironmentSpec
from .head import ValueHead
from .network import StateActionNet, StateNet


class StateCritic(CriticSpec):
    """
    Critic that learns state value functions, like V(s).
    """
    def __init__(self, state_net: StateNet, head_net: ValueHead):
        super().__init__()
        self.state_net = state_net
        self.head_net = head_net

    @property
    def num_outputs(self) -> int:
        return self.head_net.out_features

    @property
    def num_atoms(self) -> int:
        return self.head_net.num_atoms

    @property
    def distribution(self) -> str:
        return self.head_net.distribution

    @property
    def values_range(self) -> Tuple:
        return self.head_net.values_range

    @property
    def num_heads(self) -> int:
        return self.head_net.num_heads

    @property
    def hyperbolic_constant(self) -> float:
        return self.head_net.hyperbolic_constant

    def forward(self, state):
        x = self.state_net(state)
        x = self.head_net(x)
        return x

    @classmethod
    def get_from_params(
        cls,
        state_net_params: Dict,
        value_head_params: Dict,
        env_spec: EnvironmentSpec,
    ):
        state_net_params = copy.deepcopy(state_net_params)
        value_head_params = copy.deepcopy(value_head_params)

        # @TODO: any better solution?
        state_net_params["state_shape"] = env_spec.state_space.shape
        state_net = StateNet.get_from_params(**state_net_params)
        head_net = ValueHead(**value_head_params)

        net = cls(state_net=state_net, head_net=head_net)

        return net


class ActionCritic(StateCritic):
    """
    Critic that learns state-action value functions, like Q(s).
    """
    @classmethod
    def get_from_params(
        cls,
        state_net_params: Dict,
        value_head_params: Dict,
        env_spec: EnvironmentSpec,
    ):
        state_net_params = copy.deepcopy(state_net_params)
        value_head_params = copy.deepcopy(value_head_params)

        # @TODO: any better solution?
        action_space = env_spec.action_space
        assert isinstance(action_space, spaces.Discrete)
        value_head_params["out_features"] = action_space.n
        net = super().get_from_params(
            state_net_params=state_net_params,
            value_head_params=value_head_params,
            env_spec=env_spec
        )
        return net


class StateActionCritic(CriticSpec):
    """
    Critic which learns state-action value functions, like Q(s, a).
    """
    def __init__(self, state_action_net: StateActionNet, head_net: ValueHead):
        super().__init__()
        self.state_action_net = state_action_net
        self.head_net = head_net

    def forward(self, state, action):
        x = self.state_action_net(state, action)
        x = self.head_net(x)
        return x

    @property
    def num_outputs(self) -> int:
        return self.head_net.out_features

    @property
    def num_atoms(self) -> int:
        return self.head_net.num_atoms

    @property
    def distribution(self) -> str:
        return self.head_net.distribution

    @property
    def values_range(self) -> Tuple:
        return self.head_net.values_range

    @property
    def num_heads(self) -> int:
        return self.head_net.num_heads

    @property
    def hyperbolic_constant(self) -> float:
        return self.head_net.hyperbolic_constant

    @classmethod
    def get_from_params(
        cls,
        state_action_net_params: Dict,
        value_head_params: Dict,
        env_spec: EnvironmentSpec,
    ):
        state_action_net_params = copy.deepcopy(state_action_net_params)
        value_head_params = copy.deepcopy(value_head_params)

        # @TODO: any better solution?
        if isinstance(env_spec.state_space, spaces.Dict):
            state_action_net_params["state_shape"] = {
                k: v.shape
                for k, v in env_spec.state_space.spaces.items()
            }
        else:
            state_action_net_params["state_shape"] = env_spec.state_space.shape
        state_action_net_params["action_shape"] = \
            env_spec.action_space.shape
        state_action_net = StateActionNet.get_from_params(
            **state_action_net_params
        )

        value_head_params["out_features"] = 1
        head_net = ValueHead(**value_head_params)

        net = cls(state_action_net=state_action_net, head_net=head_net)

        return net


__all__ = ["CriticSpec", "StateCritic", "ActionCritic", "StateActionCritic"]
