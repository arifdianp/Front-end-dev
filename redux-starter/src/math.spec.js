import {isEven} from './math';

//demonstrate unit testing using jest

describe("isEven", () => {
  it("isEven should return true when given an even number", () => {
    const result = isEven(2);
    expect(result).toEqual(true);
  });

  it("isEven should return false when given an odd number", () => {
    const result = isEven(1);
    expect(result).toEqual(false);
  });
});
