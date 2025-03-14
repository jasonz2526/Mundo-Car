# Use Node.js as a parent image
FROM node:16

# Set the working directory inside the container
WORKDIR /app

# Copy the frontend code to the container
COPY ./frontend /app

# Install dependencies from package.json
RUN npm install

# Build the React app (or equivalent command for your frontend)
RUN npm run build

# Expose the port (default React app runs on port 3000)
EXPOSE 3000

# Start the frontend application (adjust if using different command or server)
CMD ["npm", "start"]