<template>
  <div
    class="tickers"
    v-bind:class="{
      green: deviat_week > 0,
      red: deviat_week < 0,
      green2: deviat_month > 0 && deviat_week > deviat_month,
      red2: deviat_month < 0 && deviat_week < deviat_month,
    }"
  >
    <div class="ticker desc" @click.stop="getChartUrl(ticker_id)">
      {{ ticker_name }}
    </div>
    <div class="ticker bt">
      <span class="thin" title="удалить" @click.stop="delTicker(ticker_id)"
        >x</span
      >
    </div>
    <div class="ticker id">
      {{ ticker_id }}
    </div>
    <div class="ticker deviat">
      {{ deviat_month > 0 ? "+" + deviat_month : deviat_month }}%<br />
      {{ deviat_week > 0 ? "+" + deviat_week : deviat_week }}%
    </div>
  </div>
</template>

<script>
export default {
  props: {
    ticker_id: String,
    ticker_name: String,
    deviat_month: Number,
    deviat_week: Number,
  },
  emits: ["clickDelTicker", "clickShowChart"],
  data() {
    return {};
  },
  methods: {
    delTicker() {
      this.$emit("clickDelTicker", { tickerValue: this.ticker_id });
    },
    getChartUrl() {
      this.$emit("clickShowChart", this.ticker_id);
    },
  },
};
</script>