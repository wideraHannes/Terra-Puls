FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
# Skip postinstall (nuxt prepare) — needs full source tree
RUN npm install --ignore-scripts

COPY . .

# Now run nuxt prepare with full source available
RUN npm run postinstall

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
