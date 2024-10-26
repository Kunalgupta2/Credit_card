<template>
  <div>
    <h2>Add User Income</h2>
    <form @submit.prevent="addUserIncome">
      <input
        v-model="annualIncome"
        type="number"
        placeholder="Annual Income"
        required
      />
      <button type="submit">Submit Income</button>
    </form>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      annualIncome: "",
    };
  },
  methods: {
    async addUserIncome() {
      try {
        const response = await api.post("/user_income", {
          Annual_Income: this.annualIncome.toString(),
        });
        console.log("Response:", response.data);
        alert("User income added successfully!");
        this.$router.push("/user-document");
      } catch (error) {
        console.error("Error adding user income:", error);
        console.error("Error response:", error.response);
        console.error("Error data:", error.response?.data);
        alert(
          "Failed to add user income: " +
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
