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
console.log(book.get("title"));
console.log(book.toJS());

function publish(book)
{
  return book.set("isPublished", true);
}
//needs to reassign book since book map cannot be mutated or changed inside
book = publish(book);
console.log(book.toJS());



// immer.js tutorial
let bk = {title: "harrypotter"};
// use produce to add new things value inside object
function published(bk)
{
  return produce(bk, d => {d.isPublished = true});
}
let updated = published(bk);
console.log(bk);
console.log(updated);

//create a redux import store
import store from "./store";
import {ADD, REMOVE, SOLVED} from "./actionCreator";

const unsubscribe = store.subscribe(() => {
  console.log("store has been changed!", store.getState());
});

// add action
store.dispatch(ADD("the first ever bug"));

// to disable notification on console uncomment unsubscribe
//unsubscribe();

//solved action
store.dispatch(SOLVED(1));

//remove action
store.dispatch(REMOVE());

console.log(store.getState());
