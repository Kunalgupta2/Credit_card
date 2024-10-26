<template>
  <div class="container verify-otp">
    <h2>Verify OTP</h2>
    <form @submit.prevent="verifyOTP">
      <input v-model="otp" type="text" placeholder="Enter OTP" required />
      <button type="submit">Verify OTP</button>
    </form>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      otp: "",
    };
  },
  methods: {
    async verifyOTP() {
      try {
        const sessionId = localStorage.getItem("session_id");
        if (!sessionId) {
          throw new Error("Session ID not found");
        }

        const response = await api.post("/verify_otp", {
          otp: this.otp,
          session_id: sessionId,
        });

        if (response.data === "User created successfully") {
          alert("OTP verified successfully!");
          // Remove the session ID from local storage
          localStorage.removeItem("session_id");
          // Redirect to login page
          this.$router.push("/login");
        } else {
          throw new Error("Unexpected response from server");
        }
      } catch (error) {
        console.error(
          "OTP verification error:",
          error.response?.data?.detail || error.message
        );
        alert(
          "OTP verification failed: " +
            (error.response?.data?.detail || "Unknown error")
        );
      }
    },
  },
};
</script>

<style scoped>
@import "../assets/common.css";

.verify-otp {
  max-width: 400px;
  margin: 0 auto;
  text-align: center;
}

form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

input {
  margin-bottom: 10px;
  padding: 5px;
  width: 200px;
}

button {
  padding: 5px 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>
