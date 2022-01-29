<template>
  <div v-if="!isMobile" class="card">
    <br />
    <h2 class="maintitle">Введите данные для для входа</h2>
    <div>
      Логин:
      <input
        class="login input"
        type="text"
        v-model="form_username"
        @keypress.enter="loginTo"
      />
      <div></div>
      Пароль:
      <input
        class="login input"
        type="password"
        v-model="form_password"
        @keypress.enter="loginTo"
      />
    </div>
    <br />
    <div class="card">
      <button class="btn exit" @click="loginTo">войти</button>
    </div>
  </div>

  <div v-if="isMobile" class="card mobile">
    <br />
    <h2 class="maintitle">Данные для входа</h2>
    <div>
      Логин:
      <input
        class="login input mobile"
        type="text"
        v-model="form_username"
        @keypress.enter="loginTo"
      />
      <div>
        Пароль:
        <input
          class="login input mobile"
          type="password"
          v-model="form_password"
          @keypress.enter="loginTo"
        />
      </div>
      <br />
      <div class="card mobile">
        <button class="btn exit" @click="loginTo">войти</button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  props: {
    username: String,
    password: String,
  },
  emits: ["clickBtnLogin"],
  data() {
    return {
      form_username: this.username,
      form_password: this.password,
    };
  },
  computed: {
    ...mapState({
      isMobile: "isMobile",
    }),
  },
  methods: {
    loginTo() {
      this.$emit("clickBtnLogin", {
        username: this.form_username,
        password: this.form_password,
      });
    },
  },
};
</script>