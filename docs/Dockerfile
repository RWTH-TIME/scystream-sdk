FROM python:3.12-slim AS builder

WORKDIR /project

COPY . .

RUN pip install -e .[dev]

RUN sphinx-apidoc --module-first -o /project/docs/source /project/scystream && sphinx-build -b html /project/docs/source /project/docs/build/html

FROM nginx:latest

COPY --from=builder /project/docs/build/html /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

