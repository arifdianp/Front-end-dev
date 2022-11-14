import * as actions from "./actionTypes";

export function ADD(description)
{
  return {
    type: actions.ADD,
    payload: {
      description: description
    }
  };
}

export function REMOVE()
{
  return {
    type: actions.REMOVE,
    payload: {
      id: 1
    }
  };
}

export function SOLVED(id)
{
  return {
    type: actions.SOLVED,
    payload: {
      id: id
    }
  };
}
