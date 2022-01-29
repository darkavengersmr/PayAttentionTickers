export default {
  setAuthorize(state, payload) {
    state.authorize = payload;
  },
  setMytickers(state, payload) {
    state.mytickers = payload;
  },
  setMytickersList(state, payload) {
    state.mytickersList = payload;
  },
  setUsername(state, payload) {
    state.auth.username = payload;
  },
  setPassword(state, payload) {
    state.auth.password = payload;
  },
  setToken(state, payload) {
    state.auth.token = payload;
  },
  setChart(state, payload) {
    state.chart = payload;
  },
  setChartShow(state, payload) {
    state.chartShow = payload;
  },
  setMyLog(state, payload) {
    state.mylog = payload;
  },
  setSortReverse(state, payload) {
    state.sortReverse = payload;
  },
  setAddTickerShow(state, payload) {
    state.addTickerShow = payload;
  },
  setFileUploadShow(state, payload) {
    state.fileUploadShow = payload;
  },
  setDeviat_month(state, payload) {
    state.eviat_month = payload;
  },
  setDeviat_week(state, payload) {
    state.eviat_week = payload;
  },
  setSpinnerShow(state, payload) {
    if (payload) {
      window.location.href = "#spinnerModal";
    }
    state.spinnerShow = payload;
  },
  setIsMobile(state, payload) {
    state.isMobile = payload;
  },
  setWindowinnerWidth(state, payload) {
    state.windowinnerWidth = payload;
  },
};
