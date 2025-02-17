import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { createVuetify } from "vuetify";
import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";

const app = createApp(App);
const pinia = createPinia();

const vuetify = createVuetify({
  icons: {
    iconfont: "mdi",
  },
  components,
  directives,
});

app.use(vuetify);
app.use(pinia);
app.mount("#app");
