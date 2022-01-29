<template>
  <footer class="footer">
    <br>
    <div v-if="logshow" @click.stop="logshow = !logshow" v-html="mylog" class="log"></div>
    <div v-if="!logshow" @click.stop="logshow = !logshow" class="log">
      <button class="btn danger" @click.stop="logshow = !logshow">+</button> &nbsp;
      <text>&nbsp; Показать лог событий</text>
    </div>
  </footer>
</template>


<script>
export default {
  props: {
    mylog: String
  },
  data() {
    return {
      logshow: false
    }
  }
}
</script>