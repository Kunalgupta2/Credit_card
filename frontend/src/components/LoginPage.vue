<template>
  <div class="container login-page">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input v-model="username" type="text" placeholder="Username" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <div class="button-group">
        <button type="submit">Login</button>
        <button @click="loginWithGoogle" class="google-button">
          Login with Google
        </button>
      </div>
    </form>
    <p class="register-link">
      Don't have an account?
      <a @click="$router.push('/register')">Register here</a>
    </p>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      username: "",
      password: "",
    };
  },
  methods: {
    async login() {
      try {
        const formData = new FormData();
        formData.append("username", this.username);
        formData.append("password", this.password);

        const response = await api.post("/login", formData, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });
        localStorage.setItem("access_token", response.data.access_token);
        const response2 = await api.get("/check_user_state", {
          headers: {
            Authorization: `Bearer ${response.data.access_token}`,
          },
        });
        if (response2.data === "user") {
          this.$router.push("/user-details");
        } else if (response2.data === "address") {
          this.$router.push("/user-address");
        } else if (response2.data === "income") {
          this.$router.push("/user-income");
        } else if (response2.data === "documents") {
          this.$router.push("/user-document");
        } else {
          this.$router.push("/dashboard");
        }
      } catch (error) {
        console.error(
          "Login error:",
          error.response?.data?.detail || error.message
        );
        alert(
          "Login failed: " + (error.response?.data?.detail || "Unknown error")
        );
      }
    },
    loginWithGoogle() {
      window.location.href = "/login/google"; // Redirects to your Google OAuth URL
    },
  },
};
</script>

<style scoped>
@import "../assets/common.css";

.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.google-button {
  background-color: #4285f4;
}

.google-button:hover {
  background-color: #3367d6;
}

.register-link {
  margin-top: 20px;
  text-align: center;
}

.register-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
