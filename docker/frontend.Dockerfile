FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json vite.config.js ./
COPY main/frontend ./main/frontend

ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_DOCS_BASE_URL=http://localhost:8001
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_DOCS_BASE_URL=${VITE_DOCS_BASE_URL}

RUN npm ci
RUN npm run build

FROM nginx:1.27-alpine

COPY docker/nginx.frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/main/frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
