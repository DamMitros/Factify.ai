FROM node:20-slim AS base
WORKDIR /app

COPY frontend/src/package*.json .
RUN npm ci


FROM base AS dev
WORKDIR /app

ENV NODE_ENV=development

CMD ["npm", "run", "dev"]

FROM base AS prod

COPY frontend/src/ .

ENV NODE_ENV=production

CMD ["npm", "start"]
