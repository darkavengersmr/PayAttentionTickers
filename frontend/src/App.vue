<template>
  <div class="page">
    <comp-header
      :authorize="authorize"
      :username="auth.username"
      @clickBtnExit="logOut({ vm: this })"
    />

    <main class="main">
      <login-form
        v-if="!authorize"
        :username="auth.username"
        @clickBtnLogin="
          loginTo({
            vm: this,
            username: $event.username,
            password: $event.password,
          })
        "
      />

      <div v-if="authorize" class="card">
        <br />
        <div class="title sort">
          <div><text class="maintitle">Мои тикеры</text> &nbsp;</div>

          <div v-if="!isMobile">
            <button class="btn sort" @click="addTickerModal()">
              + добавить тикер
            </button>

            <button class="btn sort" @click="fileUploadModal()">
              &#128190; Загрузить
            </button>

            <button class="btn sort" @click="exportToExcel()">
              &#128190; Сохранить
            </button>

            <button class="btn sort" @click="sortTickers()">
              &#8896;&#8897; сортировать
            </button>
          </div>

          <div v-if="isMobile">
            <button
              class="btn sort mobile"
              @click="addTickerModal()"
              title="Добавить"
            >
              +
            </button>

            <button
              class="btn sort mobile"
              @click="fileUploadModal()"
              title="Загрузить"
            >
              &#128190; &#8593;
            </button>

            <button
              class="btn sort mobile"
              @click="exportToExcel()"
              title="Сохранить"
            >
              &#128190; &#8595;
            </button>

            <button
              class="btn sort mobile"
              @click="sortTickers()"
              title="Сортировать"
            >
              &#8896;&#8897;
            </button>
          </div>
        </div>
        <br />
        <div class="map">
          <comp-ticker
            v-for="(ticker, key, idx) in mytickers"
            :ticker_id="ticker.id"
            :ticker_name="ticker.name"
            :deviat_month="ticker.deviat_month"
            :deviat_week="ticker.deviat_week"
            :key="idx"
            @clickDelTicker="
              removeTicker({ vm: this, ticker: $event.tickerValue })
            "
            @clickShowChart="getChartUrl({ vm: this, ticker: $event })"
            :title="
              getTitle(
                ticker.deviat_month,
                ticker.deviat_week,
                ticker.update_date
              )
            "
          />
        </div>
      </div>

      <chart-modal
        v-show="chartShow"
        :deviat_month="deviat_month"
        :deviat_week="deviat_week"
        :chart_url="chart"
      />

      <ticker-modal
        v-show="addTickerShow"
        :mytickersList="mytickersList"
        @closeAddModal="setAddTickerShow(!addTickerShow)"
        @clickAddTicker="
          setAddTickerShow(!addTickerShow);
          addTicker({
            vm: this,
            tickerValue: $event.tickerValue,
            descriptionValue: $event.descriptionValue,
          });
        "
      />

      <file-upload
        v-show="fileUploadShow"
        :username="auth.username"
        :password="auth.password"
        @closeUpload="closeUploadModal($event.result)"
      />

      <notifications position="top right" />

      <spinner-modal v-show="spinnerShow">
        <p>spinner</p>
      </spinner-modal>
    </main>

    <!--div v-show="spinnerShow" class="card">
      <pulse-loader></pulse-loader>
    </div-->

    <comp-footer :mylog="mylog" />
  </div>
</template>

<script>
import compHeader from "./components/Header.vue";
import loginForm from "./components/Login-form.vue";
import compTicker from "./components/Ticker.vue";
import chartModal from "./components/Chart-modal.vue";
import fileUpload from "./components/File-upload.vue";
import tickerModal from "./components/Add-ticker-modal.vue";
import compFooter from "./components/Footer.vue";
//import pulseLoader from "vue-spinner/src/PulseLoader.vue";
import spinnerModal from "./components/spinnerModal.vue";
import { mapState, mapMutations, mapActions } from "vuex";

export default {
  name: "App",
  data() {
    return {};
  },
  computed: {
    ...mapState({
      authorize: "authorize",
      mytickers: "mytickers",
      mytickersList: "mytickersList",
      hostname: "hostname",
      auth: "auth",
      chart: "chart",
      chartShow: "chart",
      mylog: "mylog",
      addTickerShow: "addTickerShow",
      fileUploadShow: "fileUploadShow",
      deviat_month: "deviat_month",
      deviat_week: "deviat_week",
      spinnerShow: "spinnerShow",
      isMobile: "isMobile",
    }),
  },
  methods: {
    ...mapMutations({
      setAuthorize: "setAuthorize",
      setUsername: "setUsername",
      setPassword: "setPassword",
      setToken: "setToken",
      setFileUploadShow: "setFileUploadShow",
      setAddTickerShow: "setAddTickerShow",
      setIsMobile: "setIsMobile",
      setWindowinnerWidth: "setWindowinnerWidth",
    }),
    ...mapActions({
      downloadMytickers: "downloadMytickers",
      downloadMytickersList: "downloadMytickersList",
      addTicker: "addTicker",
      removeTicker: "removeTicker",
      getChartUrl: "getChartUrl",
      loginTo: "loginTo",
      logOut: "logOut",
      sortTickers: "sortTickers",
      exportToExcel: "exportToExcel",
    }),
    getTitle(deviat_month, deviat_week, update_date) {
      if (deviat_month > 0) {
        deviat_month = "+" + deviat_month;
      }
      if (deviat_week > 0) {
        deviat_week = "+" + deviat_week;
      }
      return (
        "За месяц " +
        deviat_month +
        "%, за неделю " +
        deviat_week +
        "%" +
        " (обновлено " +
        update_date +
        ")"
      );
    },
    addTickerModal() {
      this.setAddTickerShow(!this.addTickerShow);
      window.location.href = "#addModal";
      this.downloadMytickersList({ vm: this });
    },
    fileUploadModal() {
      this.setFileUploadShow(!this.fileUploadShow);
      window.location.href = "#uploadModal";
    },
    closeUploadModal(result) {
      if (result === "success") {
        this.$notify({
          type: "success",
          text: "Файл отправлен",
        });
      }
      if (result === "error") {
        this.$notify({
          type: "error",
          text: "Ошибка отправки файла",
        });
      }
    },
    isMobileOrDesktop() {
      this.setWindowinnerWidth(window.innerWidth);

      if (window.innerWidth <= 1080) {
        this.setIsMobile(true);
      } else {
        if (
          /Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera Mini/i.test(
            navigator.userAgent
          )
        ) {
          this.setIsMobile(true);
        } else {
          this.setIsMobile(false);
        }
      }
    },
  },
  mounted() {
    this.loginTo({ vm: this });

    this.isMobileOrDesktop();

    window.onresize = () => {
      this.isMobileOrDesktop();
    };
  },
  components: {
    compFooter,
    compHeader,
    loginForm,
    compTicker,
    tickerModal,
    //pulseLoader,
    chartModal,
    fileUpload,
    spinnerModal,
  },
};
</script>

<style>
</style>
