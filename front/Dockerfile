FROM node:22.2.0-alpine3.20 AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install --frozen-lockfile

COPY . .

ARG NEXT_PUBLIC_API_ENDPOINT
ENV NEXT_PUBLIC_API_ENDPOINT=$NEXT_PUBLIC_API_ENDPOINT

RUN npm run build

FROM node:22.2.0-alpine3.20

WORKDIR /app

COPY --from=builder /app ./

EXPOSE 80

CMD ["npm", "run", "start", "--", "-p", "80"]
