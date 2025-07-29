# Dockerfile para el frontend SvelteKit
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

# Install wget for healthcheck
RUN apk add --no-cache wget

WORKDIR /app

# Copy built application
COPY --from=builder /app/.svelte-kit/output .svelte-kit/output/
COPY --from=builder /app/node_modules node_modules/
COPY package.json .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Run the application
CMD ["node", ".svelte-kit/output/server/index.js"]
