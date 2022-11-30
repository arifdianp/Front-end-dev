import * as actioncreate from '../api';
import * as action from '../bugs';
import store, {configStore} from '../store';
import axios from 'axios';
import Mockadapter from 'axios-mock-adapter';

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
  let fakeaxios;
  let test_store;

  beforeEach(() => {
    fakeaxios = new Mockadapter(axios);
    test_store = configStore();
  })

  const bugSlice = () => test_store.getState().entities.bugs;

  //testing for addbug function
  it("should add bug to store, if it's saved on server", async () => {
    //arrange
    const bug = {description: 'a'};
    const savedbug = {...bug, id: 1};
    fakeaxios.onPost('/bugs').reply(200, savedbug);

    //act
    await test_store.dispatch(action.addbug(bug));

    //assert
    expect(bugSlice().list).toContainEqual(savedbug);
    //expect(store.getState().entities.bugs.list).toHaveLength(1);
  });
  //testing for addbug function error case
  it("should not add bug to store, if it's not saved on server", async () => {
    //arrange
    const bug = {description: 'a'};
    fakeaxios.onPost('/bugs').reply(500);

    //act
    await test_store.dispatch(action.addbug(bug));

    //assert
    expect(bugSlice().list).toHaveLength(0);

  });

  //testing for solve bug
  it("should update solved bug, if it's saved on server", async () => {
    //arrange
    fakeaxios.onPatch('/bugs/1').reply(200, {id: 1, resolved: true});
    fakeaxios.onPost('/bugs').reply(200, {id: 1});

    //act
    await test_store.dispatch(action.addbug({}));
    await test_store.dispatch(action.solvebug(1));

    //assert
    expect(bugSlice().list[0].resolved).toEqual(true);

  });
  it("should not update solved bug, if it's not saved on server", async () => {
    //arrange
    fakeaxios.onPatch('/bugs/1').reply(500);
    fakeaxios.onPost('/bugs').reply(200, {id: 1});

    //act
    await test_store.dispatch(action.addbug({}));
    await test_store.dispatch(action.solvebug(1));

    //assert
    expect(bugSlice().list[0].resolved).not.toBe(true);
  });



  describe("loading bugs", () =>
  {
    describe("if the bug exists in the cache", () =>
    {
      it("they shouldn't be fetched from server again", async () => {
        //arrange
        fakeaxios.onGet('/bugs').reply(200, {id: 1});

        //act
        await test_store.dispatch(action.loadbugs());
        await test_store.dispatch(action.loadbugs());

        //assert
        expect(fakeaxios.history.get.length).toBe(1);
      });
    });

    describe("if the bugs don't exist in the cache", () =>
    {
      it("fetch from server and put in store", async () => {
        //arrange
        fakeaxios.onGet('/bugs').reply(200, [{id: 1}]);

        //act
        await test_store.dispatch(action.loadbugs());

        //assert
        expect(bugSlice().list).toHaveLength(1);
      });

      describe("loading indicator", () =>
      {
        it("should be true while fetching the bugs", () => {
          //arrange
          fakeaxios.onGet('/bugs').reply(() => {
            expect(bugSlice().loading).toBe(true);
            return [200, [{id:1}]];
          });

          //act
          test_store.dispatch(action.loadbugs());

        });

        it("should be false after fetching the bugs", async () => {
          //arrange
          fakeaxios.onGet('/bugs').reply(200, {id: 1});

          //act
          await test_store.dispatch(action.loadbugs());

          //assert
          expect(bugSlice().loading).toBe(false);
        });

        it("should be false if server error", () => {
          //arrange
          fakeaxios.onGet('/bugs').reply(() => {
            expect(bugSlice().loading).toBe(false);
            return [500];
          });

          //act
          test_store.dispatch(action.loadbugs());

        });
      });
    });
  });


});
