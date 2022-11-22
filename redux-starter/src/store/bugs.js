// using redux toolkit to make action code simpler
import {createSlice} from "@reduxjs/toolkit";
// reselect to
import {createSelector} from 'reselect';

let counter = 0;
const slice = createSlice({
  name: 'bugs',
  initialState: [],
  reducers: {
    ADD: (state, action) =>{
      state.push({
        id: ++counter,
        description: action.payload.description,
        resolved: false
      });
    },
    SOLVED: (state, action) =>{
      const index = state.findIndex(bug => bug.id === action.payload.id);
      state[index].resolved = true;
    },
    REMOVE: (state, action) =>{
      const index = state.findIndex(bug => bug.id === action.payload.id);
      state.pop(state[index]);
    },
    assigntoUser: (state, action) =>{
      const {bugID, userID} = action.payload;
      const index = state.findIndex(bug => bug.id === bugID);
      state[index].userID = userID;
    }
  }
});

export const {ADD, SOLVED, REMOVE, assigntoUser} = slice.actions;
export default slice.reducer;

//selector function in redux
export const getUnsolvedBugs = createSelector(
  state => state.getState().entities.bugs,
  bugs => bugs.filter(bug => !bug.resolved)
);

export const getBugbyuser = userID => createSelector(
  state => state.getState().entities.bugs,
  bugs => bugs.filter(bug => bug.userID === userID)
);
