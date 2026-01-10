# from setuptools import setup, find_packages

# with open("README.md", "r") as fh:
#     long_description = fh.read()

# setup(
#     name="sify-ai-platform",
#     version="0.0.1",
#     author="InfinitAIML",
#     description="A package for Sify's AI Platform",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     url="https://github.com/sifymdp/sify-ai-platform",
#     packages=find_packages(),
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#     ],
#     python_requires=">=3.8",
#     install_requires=[
#         "requests"
#     ],
#     extras_require={
#         "data": ["pandas","numpy"],
#         "viz": ["matplotlib","seaborn","wordcloud","plotly"],
#         "ml": ["bertopic","scikit-learn","hdbscan","umap-learn"],
#         "nlp": ["nltk", "spacy", "transformers", "sentence-transformers"],
#     },
# )

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sify-telemetry-sdk",
    version="0.1.0",
    author="Mohana Supraja",
    author_email="mohanasupraja.t@gmail.com",
    description="A lightweight telemetry SDK for traces, metrics, logs, and auto instrumentation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MohanaSupraja/sify-sdk",

    packages=find_packages(include=["sify*"]),

    python_requires=">=3.8",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        # Core
        "requests",
        "opentelemetry-api==1.38.0",
        "opentelemetry-sdk==1.38.0",
        "opentelemetry-proto==1.38.0",
        "opentelemetry-semantic-conventions==0.59b0",

        # Logging
        "opentelemetry-instrumentation-logging==0.59b0",

        # Exporters
        "opentelemetry-exporter-otlp==1.38.0",
        "opentelemetry-exporter-otlp-proto-grpc==1.38.0",
        "opentelemetry-exporter-otlp-proto-http==1.38.0",

        # Auto instrumentation core
        "opentelemetry-instrumentation==0.59b0",
        "opentelemetry-instrumentation-requests==0.59b0",
        "opentelemetry-instrumentation-urllib3==0.59b0",
        "opentelemetry-instrumentation-httpx==0.59b0",
        "opentelemetry-instrumentation-aiohttp-client==0.59b0",

        # Frameworks
        "opentelemetry-instrumentation-flask==0.59b0",
        "opentelemetry-instrumentation-fastapi==0.59b0",
        "opentelemetry-instrumentation-django==0.59b0",
        "opentelemetry-instrumentation-asgi==0.59b0",
        "opentelemetry-instrumentation-wsgi==0.59b0",

        # DB / Cache
        "opentelemetry-instrumentation-sqlalchemy==0.59b0",
        "opentelemetry-instrumentation-redis==0.59b0",
        "opentelemetry-instrumentation-pymongo==0.59b0",

        # Async
        "aiohttp>=3.8.0",
    ],

    extras_require={
        "data": [
            "pandas",
            "numpy",
        ],
        "viz": [
            "matplotlib",
            "seaborn",
            "wordcloud",
            "plotly",
        ],
        "ml": [
            "bertopic",
            "scikit-learn",
            "hdbscan",
            "umap-learn",
        ],
        "nlp": [
            "nltk",
            "spacy",
            "transformers",
            "sentence-transformers",
        ],
    },

    keywords=[
        "telemetry",
        "opentelemetry",
        "tracing",
        "metrics",
        "logging",
        "sdk",
    ],
)
