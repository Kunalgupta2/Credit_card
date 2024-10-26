<template>
  <div>
    <h2>Add User Address</h2>
    <form @submit.prevent="addUserAddress">
      <input v-model="address" type="text" placeholder="Address" required />
      <input v-model="city" type="text" placeholder="City" required />
      <input v-model="state" type="text" placeholder="State" required />
      <input v-model="country" type="text" placeholder="Country" required />
      <input
        v-model="postalCode"
        type="text"
        placeholder="Postal Code"
        required
      />
      <button type="submit">Submit Address</button>
    </form>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      address: "",
      city: "",
      state: "",
      country: "",
      postalCode: "",
    };
  },
  methods: {
    async addUserAddress() {
      try {
        const token = localStorage.getItem("access_token");
        const response = await api.post(
          "/user_address",
          {
            address: this.address,
            city: this.city,
            state: this.state,
            country: this.country,
            postal_code: this.postalCode,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        console.log(response.data);
        alert("User address added successfully!");
        this.$router.push("/user-income");
      } catch (error) {
        console.error(
          "Error adding user address:",
          error.response?.data?.detail || error.message
        );
        alert(
          "Failed to add user address: " +
            (error.response?.data?.detail || "Unknown error")
        );
      }
    },
  },
};
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

input {
  margin-bottom: 10px;
  padding: 5px;
  width: 300px;
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
