FROM python:3.10 as builder
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry export -o requirements.txt
RUN pip3 install -r requirements.txt
# for PostgreSQL
RUN pip3 install psycopg2-binary

FROM python:3.10-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . .

# -u for unbuffered output
CMD python3 -u main.py