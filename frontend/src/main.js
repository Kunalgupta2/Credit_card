import { createApp } from "vue";
import App from "./App.vue";
import router from "./router"; // Adjust the path as needed
import axios from "axios";
import "./assets/common.css";

// Optional: Set a base URL for axios
axios.defaults.baseURL = "http://localhost:8000"; // Replace with your backend URL

const app = createApp(App);

// Optionally, you can add axios to the global properties
app.config.globalProperties.$http = axios;

app.use(router);
app.mount("#app");
