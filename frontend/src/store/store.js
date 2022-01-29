import { createStore } from "vuex";

import mutations from "./mutations";
import actions from "./actions";

export default createStore({
  state() {
    return {
      authorize: false,
      spinnerShow: false,
      mytickers: [],
      sortReverse: false,
      mytickersList: [],
      auth: {
        username: "",
        password: "",
        token: "",
      },
      chart: "",
      chartShow: false,
      mylog: "",
      addTickerShow: false,
      fileUploadShow: false,
      deviat_month: 0,
      deviat_week: 0,
      isMobile: false,
      windowinnerWidth: 1920,
    };
  },
  mutations: mutations,
  actions: actions,

  getters: {},
});
