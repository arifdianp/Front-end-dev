const Joi = require('joi');
const express = require('express');
const app = express();
app.use(express.json());

// courses as mockup database
const courses = [
  {id:1, name:'a'},
  {id:2, name:'b'},
  {id:3, name:'c'}];

//http get request
app.get('/', (req,res) =>{
  res.send("Helloworld");
});

app.get('/api/courses', (req,res) =>{
  res.send(courses);
});

app.get('/api/courses/:id', (req,res) =>{
  const a = courses.find(c => c.id === parseInt(req.params.id));

  if(!a)
  {
    res.status(404).send("The course with given ID was not found");
  }
  else
  {
    res.send(a);
  }
});

//http post request
app.post('/api/courses', (req,res) =>{
  const schema = Joi.object({
    name: Joi.string().min(3).required()
  });

  const result = schema.validate(req.body);

  if(result.error)
  {
    res.status(400).send(result.error.details[0].message);
    return;
  }

  const b = {id: courses.length + 1, name: req.body.name};
  courses.push(b);
  res.send(b);
});

//http put request
app.put('/api/courses/:id', (req,res)=>{
  //look up the courses if dont exist return 404 error
  const a = courses.find(c => c.id === parseInt(req.params.id));
  if(!a)
  {
    res.status(404).send("The course with given ID was not found");
    return;
  }

  const schema = Joi.object({
    name: Joi.string().min(3).required()
  });

  const result = schema.validate(req.body);
  if(result.error)
  {
    res.status(400).send(result.error.details[0].message);
    return;
  }

  //edit the course with given ID
  a.name = req.body.name;
  res.send(a);
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`listening on port ${port}`));
