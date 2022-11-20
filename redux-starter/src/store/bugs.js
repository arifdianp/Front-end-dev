// using redux toolkit to make action code simpler
import {createSlice} from "@reduxjs/toolkit";

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
    }
  }
});

export const {ADD, SOLVED, REMOVE} = slice.actions;
export default slice.reducer;
