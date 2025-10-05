# Use the official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm install

# Copy source code
COPY frontend/src ./src
COPY frontend/public ./public

# Build the React app
RUN npm run build

# Copy the server file
COPY frontend/serve.js ./

# Expose the port the app runs on
EXPOSE 8080

# Set environment variable
ENV REACT_APP_API_URL=https://ai-stock-trading-backend-simple-1012090067429.us-central1.run.app

# Start the server
CMD ["node", "serve.js"]