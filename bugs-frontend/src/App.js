import logo from './logo.svg';
import './App.css';
import BugList from './components/BugList';
import Bugs from './components/Bugs';
import store from './store/store';
import { Provider } from 'react-redux';

function App() {
  return (
    <Provider store={store}>
      <BugList />
    </Provider>
  );
}

export default App;
