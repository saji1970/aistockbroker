# Use Node.js to serve the built React app
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install express for serving static files
RUN npm install express

# Copy built React app
COPY build/ ./build/

# Copy server script
COPY serve.js ./

# Expose port
EXPOSE 8080

# Start the server
CMD ["node", "serve.js"]
