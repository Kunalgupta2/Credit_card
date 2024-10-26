<template>
  <div class="container user-dashboard">
    <h1>User Dashboard</h1>
    <div v-if="cardDetails" class="card-details">
      <h2>Your Card Details</h2>
      <p><strong>Card Number:</strong> {{ cardDetails.card_number }}</p>
      <p><strong>Expiry Date:</strong> {{ cardDetails.expiry_date }}</p>
      <p><strong>CVV:</strong> {{ cardDetails.cvv }}</p>
      <p><strong>Spending Limit:</strong> ${{ cardDetails.spending_limit }}</p>
    </div>
    <div v-else class="create-card">
      <p>You don't have a card yet.</p>
      <button @click="createCard" :disabled="isLoading">
        {{ isLoading ? "Creating Card..." : "Create Card" }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
// import axios from "axios";
import api from "@/api/axios";

export default {
  name: "UserDashboard",
  data() {
    return {
      cardDetails: null,
      isLoading: false,
      error: null,
    };
  },
  methods: {
    async createCard() {
      this.isLoading = true;
      this.error = null;
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          console.error("Access token not found in localStorage");
        } else {
          console.log("Access token retrieved:", token);
        }
        const userData = {};

        const response = await api.post("/user_creditcard", userData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.cardDetails = response.data;
        this.$emit("card-created", this.cardDetails);
      } catch (error) {
        console.error("Error creating card:", error);
        this.error =
          error.response?.data?.detail ||
          "An error occurred while creating the card.";
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
@import "../assets/common.css";

.user-dashboard {
  text-align: center;
}

.card-details,
.create-card {
  background-color: var(--card-background);
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
}

.card-details p {
  margin: 15px 0;
  font-size: 18px;
}

.create-card p {
  margin-bottom: 20px;
  font-size: 18px;
}

.error {
  color: #d32f2f;
  margin-top: 20px;
  font-weight: bold;
}
</style>
