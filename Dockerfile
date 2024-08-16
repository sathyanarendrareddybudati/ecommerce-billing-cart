FROM node:18

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

RUN ls -la build

RUN npm install -g serve

CMD ["serve", "-s", "build"]
EXPOSE 3000