import reducer from "./bugs";
import {configureStore} from "@reduxjs/toolkit";

const store = configureStore({
  reducer
});

export default store;
