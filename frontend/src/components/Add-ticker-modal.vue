<template>
  <div>
    <div v-if="!isMobile" id="addModal" class="modal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">Добавить новый тикер</h3>
            <a
              href="#closeAddModal"
              title="Close"
              class="close"
              @click="closeTicker"
              >×</a
            >
          </div>
          <div class="modal-body">
            <div class="card">
              <div>
                Тикер: <br />
                <input
                  type="text"
                  class="input"
                  v-model="inputTickerValue"
                  @keypress.enter="addTicker"
                  @keyup="autoCompleteId"
                />
              </div>
              <div>
                Описание: <br />
                <input
                  type="text"
                  class="input"
                  v-model="inputDescriptionValue"
                  @keypress.enter="addTicker"
                  @keyup="autoCompleteName"
                />
              </div>
            </div>
            <br />
            <div class="tocenter">
              <button class="btn exit" @click="addTicker">Добавить</button>
            </div>
            <br />
            <div v-html="autocomplete"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isMobile" id="addModal" class="modal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">Добавить новый тикер</h3>
            <a
              href="#closeAddModal"
              title="Close"
              class="close"
              @click="closeTicker"
              >×</a
            >
          </div>
          <div class="modal-body">
            <div class="card">
              <div>
                Тикер: <br />
                <input
                  type="text"
                  class="input mobile"
                  v-model="inputTickerValue"
                  @keypress.enter="addTicker"
                  @keyup="autoCompleteId"
                />
              </div>
              <div>
                Описание: <br />
                <input
                  type="text"
                  class="input mobile"
                  v-model="inputDescriptionValue"
                  @keypress.enter="addTicker"
                  @keyup="autoCompleteName"
                />
              </div>
            </div>
            <br />
            <div class="tocenter">
              <button class="btn exit" @click="addTicker">Добавить</button>
            </div>
            <br />
            <div v-html="autocomplete"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  props: {
    mytickersList: Array,
  },
  emits: ["closeAddModal", "clickAddTicker"],
  data() {
    return {
      inputTickerValue: "",
      inputDescriptionValue: "",
      autocomplete: "",
    };
  },
  computed: {
    ...mapState({
      isMobile: "isMobile",
    }),
  },
  methods: {
    closeTicker() {
      this.$emit("closeAddModal");
      this.inputTickerValue = "";
      this.inputDescriptionValue = "";
      this.autocomplete = "";
    },
    addTicker() {
      this.$emit("clickAddTicker", {
        tickerValue: this.inputTickerValue,
        descriptionValue: this.inputDescriptionValue,
      });
      this.inputTickerValue = "";
      this.inputDescriptionValue = "";
      this.autocomplete = "";
    },
    autoCompleteId() {
      this.autocomplete = "";
      let index;
      for (index = this.mytickersList.length - 1; index >= 0; --index) {
        if (
          this.inputTickerValue.length > 0 &&
          this.mytickersList[index].id.indexOf(this.inputTickerValue) > -1
        ) {
          this.autocomplete +=
            "<br>" +
            this.mytickersList[index].id +
            " - " +
            this.mytickersList[index].name;
        } else if (this.inputTickerValue.length === 0) {
          this.autocomplete = "";
        }
      }

      for (index = this.mytickersList.length - 1; index >= 0; --index) {
        if (
          this.inputTickerValue.length > 0 &&
          this.mytickersList[index].id === this.inputTickerValue
        ) {
          this.inputDescriptionValue = this.mytickersList[index].name;
          break;
        } else if (this.inputTickerValue.length === 0) {
          this.inputDescriptionValue = "не найдено";
        } else if (this.mytickersList[index].id != this.inputTickerValue) {
          this.inputDescriptionValue = "не найдено";
        }
      }
    },
    autoCompleteName() {
      this.autocomplete = "";
      let index;
      for (index = this.mytickersList.length - 1; index >= 0; --index) {
        if (
          this.inputDescriptionValue.length > 0 &&
          this.mytickersList[index].name.indexOf(this.inputDescriptionValue) >
            -1
        ) {
          this.autocomplete +=
            "<br>" +
            this.mytickersList[index].id +
            " - " +
            this.mytickersList[index].name;
        } else if (this.inputTickerValue.length === 0) {
          this.autocomplete = "";
        }
      }

      for (index = this.mytickersList.length - 1; index >= 0; --index) {
        if (
          this.inputDescriptionValue.length > 0 &&
          this.mytickersList[index].name === this.inputDescriptionValue
        ) {
          this.inputTickerValue = this.mytickersList[index].id;
          break;
        } else if (this.inputDescriptionValue.length === 0) {
          this.inputTickerValue = "не найдено";
        } else if (
          this.mytickersList[index].name != this.inputDescriptionValue
        ) {
          this.inputTickerValue = "не найдено";
        }
      }
    },
  },
};
</script>

<style scoped>
body {
  font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.5;
  color: #292b2c;
  background-color: #fff;
}

/* свойства модального окна по умолчанию */
.modal {
  position: fixed; /* фиксированное положение */
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5); /* цвет фона */
  z-index: 1050;
  opacity: 0; /* по умолчанию модальное окно прозрачно */
  -webkit-transition: opacity 200ms ease-in;
  -moz-transition: opacity 200ms ease-in;
  transition: opacity 200ms ease-in; /* анимация перехода */
  pointer-events: none; /* элемент невидим для событий мыши */
  margin: 0;
  padding: 0;
}
/* при отображении модального окно */
.modal:target {
  opacity: 1; /* делаем окно видимым */
  pointer-events: auto; /* элемент видим для событий мыши */
  overflow-y: auto; /* добавляем прокрутку по y, когда элемент не помещается на страницу */
}
/* ширина модального окна и его отступы от экрана */
.modal-dialog {
  position: relative;
  width: auto;
  margin: 10px;
}
@media (min-width: 576px) {
  .modal-dialog {
    max-width: 540px;
    margin: 30px auto; /* для отображения модального окна по центру */
  }
}
/* свойства для блока, содержащего контент модального окна */
.modal-content {
  position: relative;
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  -ms-flex-direction: column;
  flex-direction: column;
  background-color: #2c3e50;
  -webkit-background-clip: padding-box;
  background-clip: padding-box;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 0.3rem;
  outline: 0;
}
@media (min-width: 768px) {
  .modal-content {
    -webkit-box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  }
}
/* свойства для заголовка модального окна */
.modal-header {
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -webkit-align-items: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: justify;
  -webkit-justify-content: space-between;
  -ms-flex-pack: justify;
  justify-content: space-between;
  padding: 15px;
  border-bottom: 1px solid #eceeef;
  background-color: #55789b;
}
.modal-title {
  margin-top: 0;
  margin-bottom: 0;
  line-height: 1;
  font-size: 1rem;
  font-weight: 500;
}
/* свойства для кнопки "Закрыть" */
.close {
  float: right;
  font-family: sans-serif;
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
  color: #000;
  text-shadow: 0 1px 0 #fff;
  opacity: 0.5;
  text-decoration: none;
}
/* свойства для кнопки "Закрыть" при нахождении её в фокусе или наведении */
.close:focus,
.close:hover {
  color: #000;
  text-decoration: none;
  cursor: pointer;
  opacity: 0.75;
}
/* свойства для блока, содержащего основное содержимое окна */
.modal-body {
  position: relative;
  -webkit-box-flex: 1;
  -webkit-flex: 1 1 auto;
  -ms-flex: 1 1 auto;
  flex: 1 1 auto;
  padding: 15px;
  overflow: auto;
}
</style>