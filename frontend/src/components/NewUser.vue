<template>
  <div class="container new-user">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input v-model="username" type="text" placeholder="Username" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <div class="button-group">
        <button type="submit">Register</button>
        <button @click="loginWithGoogle" class="google-button">
          Register with Google
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      username: "",
      email: "",
      password: "",
    };
  },
  methods: {
    async register() {
      try {
        const response = await api.post("/new_user", {
          username: this.username,
          email: this.email,
          hashed_password: this.password,
        });
        // Store the session_id and redirect to OTP verification
        localStorage.setItem("session_id", response.data.session_id);
        this.$router.push("/verify-otp");
      } catch (error) {
        console.error(
          "Registration error:",
          error.response?.data?.detail || error.message
        );
        alert(
          "Registration failed: " +
            (error.response?.data?.detail || "Unknown error")
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

.new-user {
  max-width: 500px;
  margin: 0 auto;
}

.button-group {
  display: flex;
  justify-content: space-between;
}

.google-button {
  background-color: #4285f4;
}

.google-button:hover {
  background-color: #3367d6;
}
</style>
