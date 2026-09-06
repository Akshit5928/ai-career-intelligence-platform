from __future__ import annotations

import json

from backend.app.api import run_agent_cycle


def main() -> None:
    result = run_agent_cycle()
    print(json.dumps(result, default=str))


if __name__ == "__main__":
    main()
