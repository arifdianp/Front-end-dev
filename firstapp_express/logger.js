url = 'http://logger.io/log';

const Eventemitter = require('events');

class Logger extends Eventemitter
{
  log(msg)
  {
    //send http request
    console.log(msg);

    this.emit('msg logged', {id:1, url:"http//"});
  }
}


module.exports = Logger;
//module.exports.url = url;
