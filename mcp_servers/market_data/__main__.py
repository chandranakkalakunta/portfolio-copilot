"""Allow ``PORT=8081 PYTHONPATH=mcp_servers python -m market_data`` (HTTP)."""

from market_data.server import main

if __name__ == "__main__":
    main()
