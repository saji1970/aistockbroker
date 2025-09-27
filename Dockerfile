FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json
COPY package.json .

# Install dependencies
RUN npm install

# Copy built frontend
COPY frontend/build ./frontend/build

# Copy server script
COPY server.js .

# Expose port
EXPOSE 8080

# Start the server
CMD ["npm", "start"]