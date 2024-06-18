// Function to show the popup
function showPopup() {
  document.getElementById("popup").style.display = "block";
}

// Function to close the popup
function closePopup() {
  document.getElementById("popup").style.display = "none";
}

// Function to show the upload popup
function showUploadPopup() {
  document.getElementById("uploadPopup").style.display = "block";
}

// Function to close the upload popup
function closeUploadPopup() {
  document.getElementById("uploadPopup").style.display = "none";
}

// Function to handle photo upload
function uploadPhoto() {
  event.preventDefault(); // Prevent default form submission

  // Get the file input element
  var fileInput = document.getElementById("id_userPhoto");
  if (fileInput.files.length > 0) {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("userPhotoDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("Photo Uploaded successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closeUploadPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem uploading your UserPhoto.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem uploading your UserPhoto.");
      });
  } else {
    // No file selected
    alert("Please Upload a Photo before submitting.");
  }
}

// Function to show the User Basic Details popup
function showBasicDetailsPopup() {
  document.getElementById("basicDetailsPopup").style.display = "block";
}

// Function to close the User Basic Details popup
function closeBasicDetailsPopup() {
  document.getElementById("basicDetailsPopup").style.display = "none";
}

// Function to save basic details
function saveBasicDetails() {
  event.preventDefault(); // Prevent default form submission

  // Check if the input field is empty
  var fullNameInput = document.getElementById("id_fullName");
  if (fullNameInput.value.trim() === "") {
    alert("Please fill out the full name field.");
  } else {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("basicDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("Basic details saved successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closeBasicDetailsPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem saving your basic details.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem saving your basic details.");
      });
  }
}

// Function to show the Education Details pop-up
function showEducationPopup() {
  document.getElementById("educationPopup").style.display = "block";
}

// Function to close the popup
function closeEducationPopup() {
  var popup = document.getElementById("educationPopup");
  popup.style.display = "none";
}

// Function to save Education Details
function saveEducationDetails(event) {
  event.preventDefault(); // Prevent default form submission

  var collegeName = document.getElementById("id_collegeName");
  var specialization = document.getElementById("id_specialization");
  var grade = document.getElementById("id_grade");

  // Check if any of the input fields are empty
  if (
    collegeName.value.trim() === "" ||
    specialization.value.trim() === "" ||
    grade.value.trim() === ""
  ) {
    alert("Please fill out all fields.");
  } else {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("educationDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("Education details saved successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closeEducationPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem saving your education details.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem saving your education details.");
      });
  }
}

// Function to show the Delete Education pop-up
function showdeleteducationPopup() {
  document.getElementById("deleteducationPopup").style.display = "block";
}

// Function to close the Delete Interests pop-up
function closedeleteducationPopup() {
  document.getElementById("deleteducationPopup").style.display = "none";
}

// Function to Delete Education (Sample function)
function deleteducationDetails() {
  event.preventDefault(); // Prevent default form submission

  // Get all selected checkboxes
  var checkboxes = document.querySelectorAll(
    'input[name="selected_education[]"]:checked'
  );

  // Check if no checkboxes are selected
  if (checkboxes.length === 0) {
    alert("Please select at least one education before you delete.");
  } else {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("deleteducationDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("Selected Education Feilds are deleted successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closedeleteducationPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem deleteing asked Education Feilds.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem deleteing asked Education Feilds.");
      });
  }
}

// Function to show the Interests pop-up
function showinterestsPopup() {
  document.getElementById("interestsPopup").style.display = "block";
}

// Function to close the Interests pop-up
function closeinterestsPopup() {
  document.getElementById("interestsPopup").style.display = "none";
}

// Function to save Interests (Sample function)
function saveinterestsDetails() {
  event.preventDefault(); // Prevent default form submission

  // Check if the input field is empty
  var interestsInput = document.getElementById("id_interests");
  if (interestsInput.value.trim() === "") {
    alert("Please choose interest.");
  } else {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("interestsDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("Interests saved successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closeinterestsPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem saving your Interest details.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem saving your Interest details.");
      });
  }
}

// Function to show the Delete Interests pop-up
function showdeleteinterestsPopup() {
  document.getElementById("deleteinterestsPopup").style.display = "block";
}

// Function to close the Delete Interests pop-up
function closedeleteinterestsPopup() {
  document.getElementById("deleteinterestsPopup").style.display = "none";
}

// Function to Delete Interests (Sample function)
function deleteinterestsDetails() {
  event.preventDefault(); // Prevent default form submission

  // Get all selected checkboxes
  var checkboxes = document.querySelectorAll(
    'input[name="selected_interests[]"]:checked'
  );

  // Check if no checkboxes are selected
  if (checkboxes.length === 0) {
    alert("Please select at least one interest before you delete.");
  } else {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("deleteinterestsDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("Selected interests deleted successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closedeleteinterestsPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem deleteing asked interests.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem deleteing asked interests.");
      });
  }
}

// Function to show the moreAboutUser Popup
function showmoreAboutUserPopup() {
  document.getElementById("moreAboutUserPopup").style.display = "block";
}

// Function to close the moreAboutUser pop-up
function closemoreAboutUserPopup() {
  document.getElementById("moreAboutUserPopup").style.display = "none";
}

// Function to save moreAboutUser (Sample function)
function savemoreAboutUserDetails() {
  event.preventDefault(); // Prevent default form submission

  // Check if the input field is empty
  var moreAboutuserInput = document.getElementById("id_moreAboutuser");
  if (moreAboutuserInput.value.trim() === "") {
    alert("Please fill out the More About User field.");
  } else {
    // Submit the form using AJAX or similar method to avoid page reload
    var form = document.getElementById("moreAboutUserDetailsForm");
    var formData = new FormData(form);

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          alert("More About User Data saved successfully!");

          // Clear the form fields
          form.reset();

          // Close the popup
          closemoreAboutUserPopup();

          // Redirect to avoid resubmission on page refresh
          window.location.href = window.location.href;
        } else {
          alert("There was a problem saving your More about user data.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was a problem saving your More about user data.");
      });
  }
}

function toggleButtonColor(button) {
  event.preventDefault(); // Prevent form submission
  button.classList.toggle("clicked");
}
