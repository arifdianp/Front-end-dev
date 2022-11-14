import * as actions from "./actionTypes";

let counter = 0;

//reducer function to change or manipulate the state of the data
export default function reducer(state = [], action)
{

  if(action.type == actions.ADD)
  {
    return [
      ...state,
      {
        id: ++counter,
        description: action.payload.description,
        resolved: false
      }
    ]
  }
  else if(action.type == actions.REMOVE)
  {
    return state.filter(bug => bug.id !== action.payload.id);
  }
  else if(action.type == actions.SOLVED)
  {
    return state.map(bug => bug.id !== action.payload.id? bug : {...bug, resolved: true});
  }

  return state;
}
