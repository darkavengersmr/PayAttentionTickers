import axios from "axios";
import VueCookies from "vue-cookies";

export default {
  async loginTo(context, payload) {
    context.commit("setSpinnerShow", true);
    let username = payload.username;
    let password = payload.password;
    let vm = payload.vm;

    let response = { status: 0 };

    if (username === undefined || password === undefined) {
      username = VueCookies.get("username");
      password = VueCookies.get("token");
    }

    if (!!username && !!password) {
      context.commit("setUsername", username);
      context.commit("setPassword", password);

      response = await axios
        .get("/users/", {
          auth: {
            username: this.state.auth.username,
            password: this.state.auth.password,
          },
        })
        .catch(function () {
          context.dispatch(
            "toLog",
            "Ошибка входа, неправильный логин/пароль или токен устарел"
          );
          vm.$notify({
            type: "error",
            text: "Ошибка входа, неправильный логин/пароль или токен устарел",
            duration: 3000,
          });
          context.commit("setSpinnerShow", false);
        });
    }
    if (response != undefined && response.status === 200) {
      context.commit("setAuthorize", true);
      if (response.data.method === "pwd") {
        if (response.data.token.length > 10) {
          context.commit("setToken", response.data.token);

          VueCookies.set("username", this.state.auth.username, -1);
          VueCookies.set("token", this.state.auth.token, -1);
        }
      }
      context.dispatch("toLog", "Подключение к серверу успешно");
      context.dispatch("downloadMytickers", { vm: vm });
    } else {
      context.commit("setSpinnerShow", false);
    }
  },
  logOut(context, { vm }) {
    context.commit("setUsername", "");
    context.commit("setPassword", "");
    context.commit("setAuthorize", false);
    context.dispatch("toLog", "Выход из учетной записи");
    vm.$notify({
      type: "success",
      text: "Выход из учетной записи",
    });
    VueCookies.remove("username");
    VueCookies.remove("token");
  },
  async downloadMytickersList(context, { vm }) {
    //context.commit("setSpinnerShow", true);
    let mytickerslist = await axios
      .get("/tickers/", {
        auth: {
          username: this.state.auth.username,
          password: this.state.auth.password,
        },
      })
      .catch(function () {
        context.dispatch("toLog", "Ошибка загрузки описаний тикеров");
        vm.$notify({
          type: "warn",
          text: "Ошибка загрузки описаний тикеров",
          duration: 3000,
        });
        //context.commit("setSpinnerShow", false);
      });
    context.dispatch("toLog", "Загружаем описание всех тикеров");
    context.commit("setMytickersList", mytickerslist.data);
    //context.commit("setSpinnerShow", false);
  },
  async downloadMytickers(context, { vm }) {
    context.commit("setSpinnerShow", true);
    let mytickers = await axios
      .get("/tickers/" + this.state.auth.username, {
        auth: {
          username: this.state.auth.username,
          password: this.state.auth.password,
        },
      })
      .catch(function () {
        context.dispatch("toLog", "Ошибка загрузки ваших тикеров");
        vm.$notify({
          type: "error",
          text: "Ошибка загрузки ваших тикеров",
          duration: 3000,
        });
        context.commit("setSpinnerShow", false);
      });
    context.dispatch("toLog", "Загружаем список ваших тикеров");
    context.commit("setMytickers", mytickers.data);
    context.commit("setSpinnerShow", false);
  },
  async addTicker(context, payload) {
    context.commit("setSpinnerShow", true);
    let vm = payload.vm;
    let inputTickerValue = payload.tickerValue;
    let inputDescriptionValue = payload.descriptionValue;
    let response = await axios
      .post(
        "/tickers/" + this.state.auth.username,
        {
          ticker: inputTickerValue,
          description: inputDescriptionValue,
        },
        {
          auth: {
            username: this.state.auth.username,
            password: this.state.auth.password,
          },
        }
      )
      .catch(() => {
        context.dispatch(
          "toLog",
          "Ошибка добавления тикера " + inputTickerValue
        );
        this.state.addbutton = false;
        vm.$notify({
          type: "error",
          text: "Ошибка добавления тикера",
          duration: 3000,
        });
        context.commit("setSpinnerShow", false);
      });
    if (response.status === 200) {
      context.dispatch("downloadMytickers", { vm: vm });
      context.dispatch("toLog", "Добавлен тикер " + inputTickerValue);
      vm.$notify({
        type: "success",
        text: "Добавлен тикер " + inputTickerValue,
      });
    }
    context.commit("setSpinnerShow", false);
  },
  async removeTicker(context, payload) {
    context.commit("setSpinnerShow", true);
    let vm = payload.vm;
    let ticker = payload.ticker;
    let response = await axios
      .delete("/tickers/" + this.state.auth.username + "?ticker=" + ticker, {
        auth: {
          username: this.state.auth.username,
          password: this.state.auth.password,
        },
      })
      .catch(() => {
        vm.$notify({
          type: "error",
          text: "Ошибка удаления тикера " + ticker,
          duration: 3000,
        });
        context.dispatch("toLog", "Ошибка удаления тикера " + ticker);
        context.commit("setSpinnerShow", false);
      });
    if (response.status === 200) {
      for (var i = 0; i < this.state.mytickers.length; i++) {
        if (this.state.mytickers[i].id === ticker) {
          this.state.mytickers.splice(i, 1);
        }
      }
      context.dispatch("toLog", "Удален тикер " + ticker);
      vm.$notify({
        type: "success",
        text: "Удален тикер " + ticker,
      });
    }
    context.commit("setSpinnerShow", false);
  },
  async getChartUrl(context, payload) {
    context.commit("setSpinnerShow", true);
    let vm = payload.vm;
    let ticker = payload.ticker;
    let response = await axios
      .get("/ticker/" + ticker, {
        auth: {
          username: this.state.auth.username,
          password: this.state.auth.password,
        },
      })
      .catch(function () {
        vm.$notify({
          type: "error",
          text: "Ошибка запроса графика",
          duration: 3000,
        });
        context.commit("setSpinnerShow", false);
      });

    this.state.chart = response.data.url;

    for (var i = 0; i < this.state.mytickers.length; i++) {
      if (this.state.mytickers[i].id === ticker) {
        this.state.deviat_month = this.state.mytickers[i].deviat_month;
        this.state.deviat_week = this.state.mytickers[i].deviat_week;
      }
    }
    context.dispatch("toLog", "Получаем график по тикеру " + ticker);
    this.state.chartShow = true;
    context.commit("setSpinnerShow", false);
    window.location.href = "#openModal";
  },
  toLog(context, message) {
    var now = new Date();
    let payload =
      this.state.mylog + now.toLocaleString() + "&nbsp;" + message + "<br>";
    context.commit("setMyLog", payload);
  },
  sortTickers(context) {
    let unordered = this.state.mytickers;
    if (this.state.sortReverse === false) {
      unordered.sort((a, b) =>
        a.deviat_month + a.deviat_week > b.deviat_month + b.deviat_week
          ? 1
          : b.deviat_month + b.deviat_week > a.deviat_month + a.deviat_week
          ? -1
          : 0
      );
    } else {
      unordered.sort((a, b) =>
        a.deviat_month + a.deviat_week < b.deviat_month + b.deviat_week
          ? 1
          : b.deviat_month + b.deviat_week < a.deviat_month + a.deviat_week
          ? -1
          : 0
      );
    }
    context.commit("setMytickers", unordered);
    context.commit("setSortReverse", !this.state.sortReverse);
  },
  exportToExcel() {
    axios({
      url: "/download",
      method: "GET",
      responseType: "blob",
      auth: {
        username: this.state.auth.username,
        password: this.state.auth.password,
      },
    }).then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", this.state.auth.username + ".xlsx");
      document.body.appendChild(link);
      link.click();
    });
  },
};
