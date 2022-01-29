<template>
  <div id="spinnerModal" class="modal">
    <div class="modal-dialog">
      <pulse-loader></pulse-loader>
    </div>
  </div>
</template>

<script>
import pulseLoader from "vue-spinner/src/PulseLoader.vue";
export default {
  props: {},
  data() {
    return {};
  },
  methods: {},
  components: {
    pulseLoader,
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
  display: flex;
  align-items: center;
  justify-content: center;
}
/* при отображении модального окно */
.modal:target {
  opacity: 1; /* делаем окно видимым */
  pointer-events: auto; /* элемент видим для событий мыши */
  overflow-y: auto; /* добавляем прокрутку по y, когда элемент не помещается на страницу */
}
/* ширина модального окна и его отступы от экрана */
.modal-dialog {
  width: auto;
  margin: 10px;
}
</style>