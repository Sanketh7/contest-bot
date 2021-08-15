FROM python:3.9.6 as builder
COPY requirements.txt .
# install python packages to /root/.local
RUN pip install --user -r requirements.txt

FROM python:3.9.6-alpine
RUN apk add libpq
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# -u for unbuffered output
CMD python -u main.py