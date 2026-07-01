FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build || true

# ── Production: Serve with Nginx ───────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
# Fallback: if no build output, copy source files directly
COPY --from=builder /app/index.html /usr/share/nginx/html/
COPY --from=builder /app/styles.css /usr/share/nginx/html/
COPY --from=builder /app/app.js /usr/share/nginx/html/
COPY --from=builder /app/api-client.js /usr/share/nginx/html/
COPY --from=builder /app/audio-recorder.js /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
