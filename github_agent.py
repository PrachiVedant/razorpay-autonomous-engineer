import sys
from agents import github_agent as _github_agent

sys.modules[__name__] = _github_agent
