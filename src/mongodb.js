const mongoose = require('mongoose');

// mongoose.connect("mongodb://localhost:27017/users", { useNewUrlParser: true, useUnifiedTopology: true })
//     .then(() => {
//         console.log("MongoDB connected");
//     })
//     .catch((err) => {
//         console.error("Failed to connect to MongoDB:", err);
//     });

// Connect to the first MongoDB database (usersDB)
const usersDBConnection = mongoose.createConnection("mongodb://localhost:27017/users", { useNewUrlParser: true, useUnifiedTopology: true });
usersDBConnection.on('error', err => {
    console.error("Failed to connect to usersDB:", err);
});
usersDBConnection.once('open', () => {
    console.log("Connected to usersDB");
});

// Connect to the second MongoDB database (jobsDB)
const jobsDBConnection = mongoose.createConnection("mongodb://localhost:27017/jobsdf", { useNewUrlParser: true, useUnifiedTopology: true });
jobsDBConnection.on('error', err => {
    console.error("Failed to connect to jobsDB:", err);
});
jobsDBConnection.once('open', () => {
    console.log("Connected to jobsDB");
});


//Remainign part is same
const { Schema, model } = mongoose;

const LogInSchema = new Schema({
    email: {
        type: String,
        required: true,
        unique: true,
    },
    password: {
        type: String,
        required: true,
        validate: {
            validator: function(v) {
                return /^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[a-zA-Z0-9]).{8,}$/.test(v);
            },
            message: props => `${props.value} is not a valid password! It must be at least 8 characters long, contain at least one uppercase letter, and one special character.`
        }
    },
    confirmPassword: {
        type: String,
    },
    interests: [{ type: String }],
    setup: {
        type: Number,
    },
    auidenceType: {
        type: Number,
    }
});

function generateUniqueCode() {
    // Generate a random number between 10000000 and 99999999
    const min = 10000000;
    const max = 99999999;
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
const JobSchema = new Schema({
    job_url: {
        type: String,
        required: true,
        validate: { 
            validator: function(value) {
                const urlRegex = /^(ftp|http|https):\/\/[^ "]+$/;
                return urlRegex.test(value);
            },
            message: props => `${props.value} is not a valid URL!`
        }
    },
    job_role: {
        type: String,
        required: true,
    },
    job_company: {
        type: String,
        required: true,
    },
    job_experience: {
        type: String,
    },
    job_salary: {
        type: String,
        required: true,
    },
    job_location: {
        type: String,
    },
    job_skills: {
        type: String,
    },
    job_logo: {
        type: String,
    },
    job_desc_pref1: {
        type: String,
    },
    job_desc_pref2: {
        type: String,
    },
    job_desc_pref3: {
        type: String,
    },
    job_id: {
        type: String,
        required: true,
        unique: true,
    },
}, { versionKey: false } );
const RecruiterSchema = new Schema({
    recruiterCode: {
        type: Number,
        unique: true,
        required: true,
        default: generateUniqueCode // Use the function as the default value
    },
    workemail: {
        type: String,
        unique: true,
        required: true,
    },
    password: {
        type: String,
        required: true,
    },
    contactno: {
        type: Number,
        required: true,
    },
    companyname: {
        type: String,
        required: true,
    },
    companylocation: {
        type: String,
        required: true,
    },
    companysize: {
        type: Number,
        required: true,
    },
    is_verified: {
        type: Number,
        default: 0,
    },
    verificationCode: {
        type: Number,
    },
    jobs: [JobSchema]
});

// Export all models together
// Define models for usersDB
const User = usersDBConnection.model("users", LogInSchema);
const Recruiter = usersDBConnection.model("recruiters", RecruiterSchema);

// Define models for jobsDB
const Job = jobsDBConnection.model("jobs_coll_2", JobSchema);

module.exports = {
    User,
    Recruiter,
    Job,
};
