import React, {useEffect} from 'react';
import {useDispatch, useSelector} from 'react-redux';
import * as action from '../store/bugs';

const BugList = () =>
{
  const dispatch = useDispatch();
  //copy from getUnsolvedBugs from bugs.js
  const bugs = useSelector(state => state.entities.bugs.list.filter(bug => !bug.resolved));

  useEffect(() => {
    dispatch(action.loadbugs());
  }, []);

  return(
    <ul>
      {
        bugs.map(bug => <li key={bug.id}>{bug.description}</li>)
      }
    </ul>
  );
}

export default BugList;
