import { createApp } from "vue";
import App from "./App.vue";
import store from "./store/store";
import Notifications from "@kyvg/vue3-notification";
import "./theme.css";

const app = createApp(App);

app.use(Notifications);
app.use(store);

app.mount("#app");
