from setuptools import setup, find_packages

setup(
    name="stepfun-tools",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "stepfun = stepfun.cli:main",
            "stepfun-mcp = stepfun.mcp_server:main",
        ],
    },
)
