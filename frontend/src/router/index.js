// import { createRouter, createWebHistory } from "vue-router";
// import axios from "axios";
// import LoginPage from "../components/LoginPage.vue";
// import NewUser from "../components/NewUser.vue";
// import UserDashboard from "../components/UserDashboard.vue";
// import UserDetails from "../components/UserDetails.vue";
// import UserAddress from "../components/UserAddress.vue";
// import UserIncome from "../components/UserIncome.vue";
// import UserDocument from "../components/UserDocument.vue";
// import VerifyOTP from "../components/VerifyOTP.vue";

// const routes = [
//   {
//     path: "/login",
//     component: LoginPage,
//   },
//   {
//     path: "/new-user",
//     component: NewUser,
//   },
//   {
//     path: "/dashboard",
//     component: UserDashboard,
//   },
//   {
//     path: "/user-details",
//     component: UserDetails,
//   },
//   {
//     path: "/user-address",
//     component: UserAddress,
//   },
//   {
//     path: "/user-income",
//     component: UserIncome,
//   },
//   {
//     path: "/user-document",
//     component: UserDocument,
//   },
//   {
//     path: "/verify-otp",
//     component: VerifyOTP,
//   },
// ];

// const router = createRouter({
//   history: createWebHistory(),
//   routes,
// });

// async function checkUserState() {
//   try {
//     const response = await axios.get("/check_user_state");
//     return response.data;
//   } catch (error) {
//     console.error("Error checking user state:", error);
//     return null; // or some default state
//   }
// }

// router.beforeEach(async (to, from, next) => {
//   const userState = await checkUserState();

//   if (userState === "user") {
//     next("/user-details"); // Redirect to new user page
//   } else if (userState === "address" && from.path !== "/user-address") {
//     next("/user-address"); // Redirect to user details if trying to access address directly
//   } else if (userState === "income" && from.path !== "/user-income") {
//     next("/user-income"); // Redirect to user address if trying to access income directly
//   } else if (userState === "documents" && from.path !== "/user-document") {
//     next("/user-document");
//     // Redirect to user income if trying to access documents directly
//   } else {
//     next("/dashboard"); // Allow navigation
//   }
// });

// export default router;
import { createRouter, createWebHistory } from "vue-router";
// import api from "@/api/axios";
import LoginPage from "../components/LoginPage.vue";
import NewUser from "../components/NewUser.vue";
import UserDashboard from "../components/UserDashboard.vue";
import UserDetails from "../components/UserDetails.vue";
import UserAddress from "../components/UserAddress.vue";
import UserIncome from "../components/UserIncome.vue";
import UserDocument from "../components/UserDocument.vue";
import VerifyOTP from "../components/VerifyOTP.vue";

const routes = [
  { path: "/login", component: LoginPage },
  { path: "/new-user", component: NewUser },
  { path: "/dashboard", component: UserDashboard },
  { path: "/user-details", component: UserDetails },
  { path: "/user-address", component: UserAddress },
  { path: "/user-income", component: UserIncome },
  { path: "/user-document", component: UserDocument },
  { path: "/verify-otp", component: VerifyOTP },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// async function checkUserState() {
//   try {
//     const response = await api.get("/check_user_state");
//     return response.data;
//   } catch (error) {
//     console.error("Error checking user state:", error);
//     return "/login"; // Default to login if there's an error
//   }
// }

// router.beforeEach(async (to, from, next) => {
//   const userState = await checkUserState();

//   if (userState === "user") {
//     next("/user-address");
//   } else if (userState === "address") {
//     next("/user-income");
//   } else if (userState === "income") {
//     next("/user-document");
//   } else if (userState === "documents") {
//     next("/dashboard");
//   } else {
//     next(); // Redirect to login if user state is unexpected
//   }
// });

export default router;
