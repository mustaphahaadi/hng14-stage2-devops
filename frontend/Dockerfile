FROM node:22-alpine as builder

WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev

FROM node:22-alpine as runtime

ENV NODE_ENV=production

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .

RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
		&& chown -R appuser:appgroup /app

USER appuser

EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
	CMD wget -qO- http://127.0.0.1:3000/healthz >/dev/null || exit 1

CMD ["npm", "start"]