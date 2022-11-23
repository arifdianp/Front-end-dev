const path = require('path');
var pathObj = path.parse(__filename);

const fs = require('fs');
//const files = fs.readdirSync('./');

fs.readdir('./', function(err, files){
  if (err) console.log('error', err);
  else console.log('results', files);
});

//logging message from logger.js
const Eventemitter = require('events');
const Logger = require('./logger');
const loge = new Logger();

loge.on('msg logged', function(e){
  console.log("listener called", e);
});
loge.log('msg');

//http
const http = require('http');
const server = http.createServer(function(req,res){
  if (req.url === '/')
  {
    res.write("hello world");
    res.end();
  }
});

server.on('connection', (socket) => {
  console.log('new connection');
});

server.listen(3000);
