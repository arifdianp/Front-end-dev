import {createSlice} from "@reduxjs/toolkit";
let counter = 0;
const slice = createSlice({
  name: 'user',
  initialState: [],
  reducers: {
    addUser: (state, action) =>{
      state.push({
        id: ++counter,
        name: action.payload.name
      });
    },
    removeUser: (state, action) =>{
      const index = state.findIndex(user => user.name === action.payload.name);
      state.pop(state[index]);
    }
  }
});

export const {addUser, removeUser} = slice.actions;
export default slice.reducer;
