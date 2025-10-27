FROM node:20-alpine AS base
WORKDIR /app

COPY frontend/src/package*.json .
RUN npm ci


FROM node:20-alpine AS final
WORKDIR /app

COPY frontend/src/ .

ENV NODE_ENV=development

CMD ["npm", "run", "dev"]
