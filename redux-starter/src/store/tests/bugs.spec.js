import * as actioncreate from '../api';
import * as action from '../bugs';
import store from '../store';

// describe("bugSlice", () => {
//   describe("action creators", () => {
//     it("addBug", () => {
//
//       const bug = {description: 'a'};
//       const result = action.addbug(bug);
//
//       const expected = {
//         type: actioncreate.apiReqBegin.type,
//         payload: {
//           url: '/bugs',
//           method: 'post',
//           data: bug,
//           onSuccess: action.ADD.type
//         }
//       };
//
//       expect(result).toEqual(expected);
//     });
//   });
// });

describe("bugSlice", () => {
  it("should handle the addbug action", () => {
    const bug = {description: 'a'};
    store.dispatch(action.addbug(bug));
    console.log(store.getState());
  })
});
