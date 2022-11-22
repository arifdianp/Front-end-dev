// npm i lodash
import {compose, pipe} from "lodash/fp";
//npm i immutable
import {Map} from "immutable";
//npm i immer
import {produce} from "Immer";

// Currying functional programming
let input = "  Javascript   ";
let output = "<div>" + input.trim() + "</div>";

const trim = str => str.trim();
const wrap = (type, str) => `<${type}>${str}</${type}>`;
const toLowerCase = str => str.toLowerCase();

//const transform = pipe(trim, toLowerCase, wrap("div"));
//console.log(transform(input));


//immutable.js tutorial
let book = Map({title: "harrypotter"});
//console.log(book.get("title"));
//console.log(book.toJS());

function publish(book)
{
  return book.set("isPublished", true);
}
//needs to reassign book since book map cannot be mutated or changed inside
book = publish(book);
//console.log(book.toJS());



// immer.js tutorial
let bk = {title: "harrypotter"};
// use produce to add new things value inside object
function published(bk)
{
  return produce(bk, d => {d.isPublished = true});
}
let updated = published(bk);
//console.log(bk);
//console.log(updated);

///////////////////////////////////////////////////////////////////////////////////////////////
//create a redux import store
import store from "./store/store";
import * as actions from "./store/bugs";
import {addProject} from "./store/projects";
import {addUser, removeUser} from "./store/user";

const unsubscribe = store.subscribe(() => {
  console.log("store has been changed!", store.getState());
});

// add action
//store.dispatch(actions.ADD({description:"the first ever bug"}));

// to disable notification on console uncomment unsubscribe
unsubscribe();

//solved action
//store.dispatch(actions.SOLVED({id:1}));

//remove action
//store.dispatch(actions.REMOVE({id:1}));

//store.dispatch(actions.ADD({description:"the first ever bug"}));
//store.dispatch(actions.ADD({description:"the first ever bug"}));
//store.dispatch(actions.SOLVED({id:3}));

//store.dispatch(addUser({name: "user1"}));
//store.dispatch(addUser({name: "user2"}));
//store.dispatch(actions.assigntoUser({bugID: 2, userID: 1}));

//const x = actions.getUnsolvedBugs(store);

//console.log(actions.getBugbyuser(2)(store));

//store.dispatch({type: 'error', payload: {message: 'erroror'}});

// add bug in UI layer
//store.dispatch(actions.addbug({description: 'a'}));

// getting bugs info to UI layer or frontend
store.dispatch(actions.loadbugs());
//setTimeout(() => store.dispatch(actions.solvebug(1)), 2000);
setTimeout(() => store.dispatch(actions.assignBugtouser(1, 4)), 3000);
