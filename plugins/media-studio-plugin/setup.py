from setuptools import setup, find_packages

setup(
    name="media-studio-tools",
    version="1.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "media-studio = media_studio.cli:main",
            "media-studio-mcp = media_studio.mcp_server:main",
        ],
    },
)
