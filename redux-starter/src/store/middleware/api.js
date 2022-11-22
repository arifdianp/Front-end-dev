//npm i axios
import axios from "axios";
//import actions from api configureStore
import * as actions from '../api';

//if use await action must be async
const api = store => next => async action =>{
  if(action.type !== actions.apiReqBegin.type)
    return next(action);

  const {url, method, data, onStart, onSuccess, onError} = action.payload;

  if(onStart)
    store.dispatch({type: onStart});

  next(action);

  try{
    //mockup calling api since it's mockup its imitated as strings.
    const response = await axios.request({
      baseURL: 'http://localhost:9001/api/',
      url,
      method,
      data
    });

    //dispatch an action for successful api request
    store.dispatch(actions.apiReqSuccess(response.data));

    //specific success action
    if(onSuccess)
      store.dispatch({type: onSuccess, payload: response.data});
  }
  catch(error){
    store.dispatch(actions.apiReqFailed(error.message));

    //specific failure action
    if(onError)
      store.dispatch({type: onError, payload: error.message});
  }
};

export default api;
