import React, {Component} from 'react';
import *  as action from '../store/bugs';
import { Provider } from 'react-redux';
import { connect } from 'react-redux';

class Bugs extends Component
{
  //state = {bugs: []};

  componentDidMount()
  {
    this.props.loadbugs();
  }


  render()
  {
    return (
      <ul>
        {
          this.props.bugs.map(bug => <li key={bug.id}>{bug.description}</li>)
        }
      </ul>
    );
  }
}

//state.entities.bugs.list
const mapstatetoprops = state => ({
  bugs: state.entities.bugs.list
});

const mapdispatchtoprops = dispatch => ({
  loadbugs: () => dispatch(action.loadbugs())
});

export default connect(mapstatetoprops, mapdispatchtoprops)(Bugs)
