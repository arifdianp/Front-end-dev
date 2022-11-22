import {combineReducers} from 'redux';
import bugsreducer from './bugs';
import projectreducer from './projects';
import userreducer from './user';

export default combineReducers({
  bugs: bugsreducer,
  projects: projectreducer,
  user: userreducer
});
