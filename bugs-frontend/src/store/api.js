import {createAction} from '@reduxjs/toolkit';

export const apiReqBegin = createAction('api/ReqBegin');
export const apiReqSuccess = createAction('api/ReqSuccess');
export const apiReqFailed = createAction('api/ReqFailed');
