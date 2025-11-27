FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY package.json .
COPY . .

RUN apk add --no-cache nodejs npm && \
    npm install && \
    npm run build

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]