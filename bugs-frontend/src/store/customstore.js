import reducer from "./bugs";

function createStore(reducer)
{
  let state;
  let listeners = [];

  function getState()
  {
    return state;
  }

  function dispatch(action)
  {
    state = reducer(state, action);

    for(let i=0; i < listeners.length; i++)
    {
      listeners[i]();
    }
  }

  function subscribe(listener)
  {
    listeners.push(listener);
  }

  return{
    subscribe,
    dispatch,
    getState
  };

};

export default createStore(reducer);
