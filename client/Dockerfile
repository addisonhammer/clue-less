FROM node:10

RUN npm i npm@latest -g

RUN mkdir /opt/app && chown node:node /opt/app
WORKDIR /opt/app

# install dependencies in container
USER node
COPY ./client/package.json ./client/package-lock.json ./
RUN npm install --no-optional && npm cache clean --force
ENV PATH /opt/app/node_modules/.bin:$PATH

WORKDIR /opt/app/src
COPY ./client/src .

WORKDIR /opt/app/public
COPY ./client/public .