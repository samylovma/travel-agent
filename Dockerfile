FROM python:3.12-alpine AS builder

RUN apk add --no-cache curl

ENV PDM_HOME=/opt/pdm
RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -

WORKDIR /tmp/travel-agent
COPY pyproject.toml pdm.lock README.md MANIFEST.in .
COPY src/ src/

RUN $PDM_HOME/bin/pdm sync --no-editable --production


FROM python:3.12-alpine

COPY --from=builder /tmp/travel-agent/.venv /opt/travel-agent

CMD ["/opt/travel-agent/bin/python", "-m", "travel_agent"]
