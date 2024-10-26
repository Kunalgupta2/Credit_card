<template>
  <div class="container user-document">
    <h2>Upload Documents</h2>
    <form @submit.prevent="uploadDocuments" enctype="multipart/form-data">
      <div class="camera-section">
        <video ref="video" width="320" height="240" autoplay></video>
        <canvas
          ref="canvas"
          width="320"
          height="240"
          style="display: none"
        ></canvas>
        <button type="button" @click="capturePhoto" class="capture-button">
          Capture Photo
        </button>
        <img
          v-if="capturedImage"
          :src="capturedImage"
          alt="Captured photo"
          class="captured-image"
        />
      </div>
      <div class="file-upload">
        <input
          type="file"
          @change="handleFileUpload('license', $event)"
          required
        />
      </div>
      <button type="submit">Upload Documents</button>
    </form>
    <div v-if="showPopup" class="popup">
      <div class="popup-content">
        <h3>{{ popupTitle }}</h3>
        <p>{{ popupMessage }}</p>
        <button @click="closePopup">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/api/axios";

export default {
  data() {
    return {
      photo: null,
      license: null,
      capturedImage: null,
      stream: null,
      showPopup: false,
      popupTitle: "",
      popupMessage: "",
    };
  },
  mounted() {
    this.startCamera();
  },
  beforeUnmount() {
    this.stopCamera();
  },
  methods: {
    startCamera() {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          this.stream = stream;
          this.$refs.video.srcObject = stream;
        })
        .catch((error) => {
          console.error("Error accessing camera:", error);
          this.showErrorPopup(
            "Camera Error",
            "Unable to access camera. Please make sure you've granted permission."
          );
        });
    },
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach((track) => track.stop());
      }
    },
    capturePhoto() {
      const context = this.$refs.canvas.getContext("2d");
      context.drawImage(this.$refs.video, 0, 0, 320, 240);
      this.capturedImage = this.$refs.canvas.toDataURL("image/jpeg");
      this.photo = this.dataURLtoFile(this.capturedImage, "captured_photo.jpg");
    },
    dataURLtoFile(dataurl, filename) {
      let arr = dataurl.split(","),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, { type: mime });
    },
    handleFileUpload(type, event) {
      this[type] = event.target.files[0];
    },
    async uploadDocuments() {
      if (!this.photo || !this.license) {
        this.showErrorPopup(
          "Missing Documents",
          "Please capture a photo and upload a license document."
        );
        return;
      }

      const token = localStorage.getItem("access_token");
      const formData = new FormData();
      formData.append("photo", this.photo);
      formData.append("license", this.license);
      try {
        const response = await api.post("/user_document", formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        });
        console.log(response.data);
        if (response.data.message === "User document added successfully") {
          this.showSuccessPopup("Success", "Documents uploaded successfully!");
          setTimeout(() => {
            this.$router.push("/dashboard");
          }, 2000);
        } else {
          this.showErrorPopup(
            "Upload Failed",
            response.data.verification_summary ||
              "Failed to upload documents. Please try again."
          );
        }
      } catch (error) {
        console.error("Error uploading documents:", error);
        console.error("Error response:", error.response);
        console.error("Error data:", error.response?.data);
        this.showErrorPopup(
          "Upload Failed",
          error.response?.data?.detail ||
            "Failed to upload documents. Please try again."
        );
      }
    },
    showSuccessPopup(title, message) {
      this.popupTitle = title;
      this.popupMessage = message;
      this.showPopup = true;
    },
    showErrorPopup(title, message) {
      this.popupTitle = title;
      this.popupMessage = message;
      this.showPopup = true;
    },
    closePopup() {
      this.showPopup = false;
    },
  },
};
</script>

<style scoped>
@import "../assets/common.css";

.user-document {
  max-width: 600px;
}

.camera-section {
  margin-bottom: 20px;
}

.capture-button {
  margin-top: 10px;
}

.captured-image {
  max-width: 100%;
  margin-top: 10px;
}

.file-upload {
  margin-bottom: 20px;
}

.popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.popup-content {
  background-color: var(--card-background);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}
</style>
