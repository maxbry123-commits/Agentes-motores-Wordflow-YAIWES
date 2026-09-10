# Evaluation sandbox image for MatTools RealWorld tasks.
#
# The project-level requirements.txt is exported for Python 3.13 and contains
# environment markers that pip skips on this Python 3.11 base image. Installing
# that file here produces an image without pymatgen/numpy. Keep this sandbox
# explicit and minimal: it only needs the libraries that generated functions
# import during result_analysis.py plus package-index dependencies and the bundled pymatgen source code.
FROM python:3.11.8

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m pip install --upgrade pip && \
    python -m pip install \
      numpy==1.26.4 \
      pandas==2.2.2 \
      matplotlib==3.10.0 \
      ase==3.23.0 \
      pymatgen==2024.8.9 \
      pymatgen-analysis-defects==2024.7.19 \
      phonopy==2.38.2 \
      openpyxl==3.1.5

# Code-only release: copy source corpus only; heavyweight fixture data is external.
COPY src/tool_source_code/pymatgen/src /app/tool_source_code/pymatgen/src

CMD ["bash"]
