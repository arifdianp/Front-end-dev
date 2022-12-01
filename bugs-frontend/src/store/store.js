import reducer from "./reducer";
import {configureStore, getDefaultMiddleware} from "@reduxjs/toolkit";
import logger from "./middleware/logger";
import func from "./middleware/func";
import toast from "./middleware/toast";
import api from "./middleware/api";

const store = configureStore({
  reducer,
  middleware: [
    ...getDefaultMiddleware(),
    logger({destination: "console"}),
    func,
    toast,
    api
  ]
});

function configStore() {
  return configureStore({
    reducer,
    middleware: [
      ...getDefaultMiddleware(),
      //logger({destination: "console"}),
      func,
      toast,
      api
    ]
  });
}

export default store;
export {configStore};
