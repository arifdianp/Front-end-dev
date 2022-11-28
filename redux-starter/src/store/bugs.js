// using redux toolkit to make action code simpler
import {createSlice} from "@reduxjs/toolkit";
// reselect to
import {createSelector} from 'reselect';

import axios from 'axios';

//import action from api store
import {apiReqBegin} from './api';
//import moment for time calculation
import moment from 'moment';




const slice = createSlice({
  name: 'bugs',
  initialState: {
    list: [],
    loading: false,
    lastFetch: null
  },
  reducers: {
    ADD: (state, action) =>{
      state.list.push(action.payload);
    },
    SOLVED: (state, action) =>{
      const index = state.list.findIndex(bug => bug.id === action.payload.id);
      state.list[index].resolved = true;
    },
    REMOVE: (state, action) =>{
      const index = state.list.findIndex(bug => bug.id === action.payload.id);
      state.list.pop(state[index]);
    },
    assigntoUser: (state, action) =>{
      const {id: bugID, userID} = action.payload;
      const index = state.list.findIndex(bug => bug.id === bugID);
      state.list[index].userID = userID;
    },
    bugreceived: (state,action) =>{
      state.list = action.payload;
      state.loading = false;
      state.lastFetch = Date.now();
    },
    bugrequested: (state,action) =>{
      state.loading = true;
    },
    bugrequestfail: (state,action) =>{
      state.loading = false;
    }
  }
});

//do not export this inner function to prevent unintentional usage in UI call
export const {ADD, SOLVED, REMOVE, assigntoUser, bugreceived, bugrequested, bugrequestfail} = slice.actions;
export default slice.reducer;



//action creators
// load the bugs from API
export const loadbugs = () => (dispatch, getState) => {
  const time_record = getState().entities.bugs.lastFetch;
  const time_difference = moment().diff(moment(time_record), 'minutes');
  if(time_difference < 10) return;

  dispatch(
    apiReqBegin({
      url: '/bugs',
      onStart: bugrequested.type,
      onSuccess: bugreceived.type,
      onError: bugrequestfail.type
    })
  );
};

// Adding bug command exported to UI layer
export const addbug = (bug) => {
  try
  {
    const response = axios.post(url, bug);
    dispatch(ADD(bug));
  }
  catch(error)
  {
    dispatch({type: 'error'});
  }
};

// export const addbug = (bug) => apiReqBegin({
//   url: '/bugs',
//   method: 'post',
//   data: bug,
//   onSuccess: ADD.type
// });

export const solvebug = (id) => apiReqBegin({
  url:'/bugs' + '/' + id,
  method: 'patch',
  data: {resolved: true},
  onSuccess: SOLVED.type
});

export const assignBugtouser = (bugID, userID) => apiReqBegin({
  url:'/bugs' + '/' + bugID,
  method: 'patch',
  data: {userID},
  onSuccess: assigntoUser.type
});



//selector function in redux
export const getUnsolvedBugs = createSelector(
  state => state.getState().entities.bugs,
  bugs => bugs.filter(bug => !bug.resolved)
);

export const getBugbyuser = userID => createSelector(
  state => state.getState().entities.bugs,
  bugs => bugs.filter(bug => bug.userID === userID)
);
