<template>
  <div class="container user-details">
    <h2>Add User Details</h2>
    <form @submit.prevent="addUserDetails">
      <input
        v-model="firstName"
        type="text"
        placeholder="First Name"
        required
      />
      <input v-model="lastName" type="text" placeholder="Last Name" required />
      <input
        v-model="phoneNumber"
        type="text"
        placeholder="Phone Number"
        required
      />
      <input
        v-model="dateOfBirth"
        type="date"
        placeholder="Date of Birth"
        required
      />
      <select v-model="gender" required>
        <option disabled value="">Select Gender</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
        <option value="other">Other</option>
      </select>
      <button type="submit">Submit Details</button>
    </form>
    <button @click="$router.push('/dashboard')" class="back-button">
      Back to Dashboard
    </button>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      firstName: "",
      lastName: "",
      phoneNumber: "",
      dateOfBirth: "",
      gender: "",
    };
  },
  methods: {
    async addUserDetails() {
      try {
        const token = localStorage.getItem("access_token");
        // Convert dateOfBirth from yyyy-mm-dd to dd-mm-yyyy

        const userData = {
          first_name: this.firstName,
          last_name: this.lastName,
          phone_number: this.phoneNumber,
          date_of_birth: this.dateOfBirth, // Use the formatted date
          gender: this.gender,
        };
        console.log("Sending user data:", userData);
        const response = await api.post("/user_details", userData, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        console.log("Response:", response.data);
        alert("User details added successfully!");
        this.$router.push("/user-address");
      } catch (error) {
        console.error("Error adding user details:", error);
        console.error("Error response:", error.response);
        console.error("Error data:", error.response?.data);
        alert(
          "Failed to add user details: " +
            (error.response?.data?.detail || "Unknown error")
        );
      }
    },
  },
};
</script>

<style scoped>
@import "../assets/common.css";

.user-details {
  max-width: 500px;
}

.back-button {
  margin-top: 20px;
  background-color: var(--primary-color);
}

.back-button:hover {
  background-color: var(--secondary-color);
}
</style>
