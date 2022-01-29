<template>
  <header v-if="authorize" class="header">
    <div v-if="!isMobile"><h2>PayAttentionTickers</h2></div>
    <div v-if="isMobile"><h3>PayAttentionTickers</h3></div>
    <div v-if="!isMobile">
      Пользователь: {{ username }} &nbsp;
      <button class="btn exit" v-on:click="btnExit()">выход</button>
    </div>
    <div v-if="isMobile">
      {{ username }} <br />
      <button class="btn exit mobile" v-on:click="btnExit()">выход</button>
    </div>
  </header>
  <header v-if="!authorize" class="header">
    <div v-if="!isMobile"><h2>PayAttentionTickers</h2></div>
    <div v-if="isMobile"><h3>PayAttentionTickers</h3></div>
    <div>&nbsp;</div>
  </header>
</template>


<script>
import { mapState } from "vuex";
export default {
  props: {
    authorize: Boolean,
    username: String,
  },
  emits: ["clickBtnExit"],
  data() {
    return {};
  },
  computed: {
    ...mapState({
      isMobile: "isMobile",
    }),
  },
  methods: {
    btnExit() {
      this.$emit("clickBtnExit");
    },
  },
};
</script>