const express = require('express');
const app = express(); 
const path = require('path');
const { User, Recruiter, Job } = require("./mongodb");

const tempelatePath = path.join(__dirname, '../templetes');
const crypto = require('crypto');
const { exec } = require('child_process');
const nodemailer = require('nodemailer');
// Serve static files from the 'public' directory
app.use(express.static('public'));

// Serve images from the 'images' directory
app.use('/images', express.static('images'));

const session = require('express-session');
const generateRandomString = (length) => {
    return crypto.randomBytes(Math.ceil(length / 2))
        .toString('hex')
        .slice(0, length);
};

const secretKey = generateRandomString(32); 

console.log(secretKey);

app.use(express.json());
app.set("view engine", "hbs");
app.set("views", tempelatePath);
app.use(express.urlencoded({ extended: false }));
app.use(session({
    secret: secretKey,
    resave: false,
    saveUninitialized: false
}));



app.get("/", (req, res) => {
  res.render("landingPage");
});
app.get("/about", (req, res) => {
    res.render("about");
  });
app.get("/option_page", (req, res) => {
    res.render("option_page");
  });
app.get("/login", (req, res) => {
    res.render("login");
});
app.get("/signup", (req, res) => {
    res.render("signup");
});
app.get("/recruiter_login", (req, res) => {
    res.render("recruiter_login");
});
app.get("/recruiter_signup", (req, res) => {
    res.render("recruiter_signup");
});
app.get("/question", (req, res) => {
    res.render("question");
});
app.post("/question", async (req, res) => {
    res.render("question");
});
app.get("/before12thquestion", (req, res) => {
    res.render("before12thquestion");
 });
 app.post("/before12thquestion", (req, res) => {
    res.render("before12thquestion");
 });
 app.get("/9_10thinterest", (req, res) => {
    res.render("9_10thinterest");
 });
 app.get("/11_12thinterest", (req, res) => {
    res.render("11_12thinterest");
 });
app.get("/interest", (req, res) => {
    res.render("interest");
});

app.post("/interest", async (req, res) => {
    const email = req.session.email; 
    const interests = req.body.interests; 

    try {
        const user = await User.findOne({ email: email });

        if (!user) {
            return res.status(400).send("User not found.");
        }

      
        interests.forEach(interest => {
            if (!user.interests.includes(interest)) {
                user.interests.push(interest);
            }
        });

        user.setup = 1; 
        user.auidenceType = 1;

        await user.save();
        return res.redirect("/main");
    } catch (error) {
        console.error("Error occurred while saving interests:", error);
        res.status(500).send("Internal Server Error.");
    }
});
app.post("/9_10thinterest", async (req, res) => {
    const email = req.session.email; 
    const interests = req.body.interests; 

    try {
        const user = await User.findOne({ email: email });

        if (!user) {
            return res.status(400).send("User not found.");
        }

      
        interests.forEach(interest => {
            if (!user.interests.includes(interest)) {
                user.interests.push(interest);
            }
        });

        user.setup = 1;
        user.auidenceType = 2; 

        await user.save();
        return res.redirect("/before12th");
    } catch (error) {
        console.error("Error occurred while saving interests:", error);
        res.status(500).send("Internal Server Error.");
    }
});
app.post("/11_12thinterest", async (req, res) => {
    const email = req.session.email; 
    const interests = req.body.interests; 

    try {
        const user = await User.findOne({ email: email });

        if (!user) {
            return res.status(400).send("User not found.");
        }

      
        interests.forEach(interest => {
            if (!user.interests.includes(interest)) {
                user.interests.push(interest);
            }
        });

        user.setup = 1; 
        user.auidenceType = 2;

        await user.save();
        return res.redirect("/before12th");
    } catch (error) {
        console.error("Error occurred while saving interests:", error);
        res.status(500).send("Internal Server Error.");
    }
});
app.get('/before12th', async (req, res) => {
    const email = req.session.email;
    if (!email) {
        return res.send("Email not found in session");
    }
    res.redirect(`http://127.0.0.1:5001/before12th?email=${email}`);
});
app.get("/error", (req, res) => {
    res.render("interest");
});
app.get("/email_verified", (req, res) => {
    res.render("email_verified");
});
app.get('/jobpost', async (req, res) => {
    try {
        const workemail = req.session.workemail;
        if (!workemail) {
            return res.render('error', { message: 'workemail not found in session.' });
        }

        const recruiter = await Recruiter.findOne({ workemail: workemail }).exec();
        if (!recruiter) {
            return res.render('error', { message: 'Recruiter not found.' });
        }

        const jobs = recruiter.jobs;

        res.render('jobpost', { jobs: jobs, workemail: workemail });
    } catch (error) {
        console.error('Error fetching jobs:', error);
        res.render('error', { message: 'An error occurred while fetching jobs.' });
    }
});
app.get('/profile', async (req, res) => {
    try {
        const workemail = req.session.workemail;
        if (!workemail) {
            return res.render('error', { message: 'Work email not found in session.' });
        }

        const recruiter = await Recruiter.findOne({ workemail: workemail }).exec();
        if (!recruiter) {
            return res.render('error', { message: 'Recruiter not found.' });
        }

        res.render('profile', { recruiter: recruiter });
    } catch (error) {
        console.error('Error fetching profile:', error);
        res.render('error', { message: 'An error occurred while fetching profile data.' });
    }
});

app.get('/postjob', async (req, res) => {
    try {
        const workemail = req.session.workemail;

        
        if (!workemail) {
            return res.render('error', { message: 'workemail not found in route parameters.' });
        }

        res.render('postjob', { workemail: workemail });
    } catch (err) {
        console.error('Error rendering postjob page:', err);
        res.render('error', { message: 'An error occurred.' });
    }
});

app.post('/postjob', async (req, res) => {

    const workemail = req.session.workemail; 

    console.log("Work Email:", workemail);

    // Find the last job in the database
    const lastJob = await Job.findOne({}, {}, { sort: { 'job_id': -1 }});

    // Extract the last job_id and increment it
    let lastJobId = 1;
    if (lastJob) {
        lastJobId = parseInt(lastJob.job_id.slice(1)) + 1;
    }

    // Format the new job_id
    const job_id = "j" + lastJobId.toString().padStart(5, '0');
    console.log("Generated Job ID:", job_id);
    const data = {
        job_url: req.body.job_url,
        job_role: req.body.job_role,
        job_company: req.session.companyname,
        job_experience: req.body.job_experience,       
        job_salary: req.body.job_salary,
        job_location: req.body.job_location,
        job_skills: req.body.job_skills,
        job_logo: "/static/images/gslogo2_dark.png",
        job_desc_pref1: req.body.job_desc,
        job_desc_pref2: "", 
        job_desc_pref3: "",
        job_id: job_id,
    };

    try {
        const recruiter = await Recruiter.findOne({ workemail: workemail });

        if (!recruiter) {
            return res.status(404).send("Recruiter not found");
        }

        const existingJob = recruiter.jobs.find(job => 
            job.job_id === data.job_id &&
            job.job_company === data.job_company &&
            job.job_salary === data.job_salary &&
            job.job_url === data.job_url
        );

        if (existingJob) {
            console.log("Job already exists.");
            return res.status(400).send("Job already exists."); 
        }
        recruiter.jobs.push(data);
        await recruiter.save();

        // 3. Insert the job data into the job_coll_2 collection
        // Create a new job document using the Job model
        const newJob = new Job({
            job_url: data.job_url,
            job_role: data.job_role,
            job_company: data.job_company,
            job_experience: data.job_experience,
            job_salary: data.job_salary,
            job_location: data.job_location,
            job_skills: data.job_skills,
            job_logo: data.job_logo,
            job_desc_pref1: data.job_desc_pref1,
            job_desc_pref2: data.job_desc_pref2,
            job_desc_pref3: data.job_desc_pref3,
            job_id: data.job_id,
        });

        // Save the new job document to the database
        await newJob.save();

        console.log("Job posted successfully.");
        res.redirect("/jobpost");
    } catch (error) {
        console.error("Error occurred while posting job:", error); 
        res.status(500).send("Internal Server Error."); 
    }
});



app.get('/view_job/:_id', async (req, res) => {
    const job_id = req.params._id;
    try {
        const workemail = req.session.workemail;
        if (!workemail) {
            return res.render('error', { message: 'Workemail not found in session.' });
        }

        const recruiter = await Recruiter.findOne({ workemail: workemail }).exec();
        if (!recruiter) {
            return res.render('error', { message: 'Recruiter not found.' });
        }
        const job = recruiter.jobs.find(job => job._id.toString() === job_id);
        if (job) {
            res.render('view_job', { job }); 
        } else {
            return res.render('error', { message: 'Job not found.' });
        }
    } catch (err) {
        console.error('Error fetching job details:', err);
        res.status(500).send('Internal Server Error');
    }
});

app.post('/view_job/:_id', async (req, res) => {
    const jobId = req.params._id;
    try {
        
        const updatedJob = req.body;

        if (typeof updatedJob !== 'object' || updatedJob === null) {
            throw new Error('Invalid job data');
        }

        const recruiter = await Recruiter.findOne({ 'jobs._id': jobId });
        if (!recruiter) {
            return res.status(404).render('error', { message: 'Recruiter not found.' });
        }

        const jobIndex = recruiter.jobs.findIndex(job => job._id.toString() === jobId);
        if (jobIndex === -1) {
            return res.status(404).render('error', { message: 'Job not found.' });
        }

        const jobToUpdate = recruiter.jobs[jobIndex];
        for (const key in updatedJob) {
            if (Object.prototype.hasOwnProperty.call(updatedJob, key)) {
                jobToUpdate[key] = updatedJob[key];
            }
        }
        await recruiter.save();

        // the jobsdf part 
        const job = recruiter.jobs.find(job => job._id.toString() === jobId);
        console.log('Job:', job);

        // Now, let's update the job in another collection (Job)
        await Job.updateOne({ job_url: job.job_url }, { $set: updatedJob });
        
        res.redirect(`/jobpost`);
    } catch (err) {
        console.error('Error updating job details:', err);
        res.status(500).render('error', { message: 'Internal Server Error' });
    }
});

app.get('/deletejob/:id', async (req, res) => {
    const jobId = req.params.id;

    try {
        const workemail = req.session.workemail;
        if (!workemail) {
            return res.status(404).json({ message: 'Workemail not found in session' });
        }

        const recruiter = await Recruiter.findOne({ workemail }).exec();
        console.log('Recruiter:', recruiter); 

        if (!recruiter) {
            return res.status(404).json({ message: 'Recruiter not found' });
        }

        const job = recruiter.jobs.find(job => job._id.toString() === jobId);
        console.log('Job:', job);

        if (!job) {
            return res.status(404).json({ message: 'Job not found' });
        }

        const deletedJob = await Recruiter.findOneAndUpdate(
            { workemail },
            { $pull: { jobs: { _id: jobId } } }, // Using job_url field instead of _id
            { new: true }
        );

        
        const jobUrl = job.job_url;
        // Delete the job from the second database using job_url
        const deletedJobFromJobDB = await Job.deleteOne({ job_url: jobUrl }); // Using job_url field instead of _id

        if (deletedJob) {
            console.log("Job deleted successfully");
            // res.status(200).json({ message: 'Job deleted successfully' });
        } else {
            // Error deleting job
            res.status(500).json({ message: 'Error deleting job' });
        }
    } catch (error) {
        // Error handling
        console.error('Error deleting job:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
});
app.get('/edit_profile/:_id', async (req, res) => {
    const recruiterId = req.params._id;
    try {
        const workemail = req.session.workemail;
        if (!workemail) {
            return res.render('error', { message: 'Workemail not found in session.' });
        }

        const recruiter = await Recruiter.findOne({ _id: recruiterId, workemail: workemail }).exec();
        if (!recruiter) {
            return res.render('error', { message: 'Recruiter not found.' });
        }

        res.render('edit_profile', { recruiter });
    } catch (err) {
        console.error('Error fetching profile details:', err);
        res.status(500).send('Internal Server Error');
    }
});

app.post('/edit_profile/:_id', async (req, res) => {
    const recruiterId = req.params._id;
    try {
        const updatedProfile = req.body;

        if (typeof updatedProfile !== 'object' || updatedProfile === null) {
            throw new Error('Invalid profile data');
        }

        const recruiter = await Recruiter.findOne({ _id: recruiterId, 'workemail': req.session.workemail });
        if (!recruiter) {
            return res.status(404).render('error', { message: 'Recruiter not found.' });
        }

        for (const key in updatedProfile) {
            if (Object.prototype.hasOwnProperty.call(updatedProfile, key)) {
                recruiter[key] = updatedProfile[key];
            }
        }

        await recruiter.save();

        res.redirect(`/profile`);
    } catch (err) {
        console.error('Error updating profile details:', err);
        res.status(500).render('error', { message: 'Internal Server Error' });
    }
});

const verifyMail = async (req, res) => {
    try {
        // Extract the verification code entered by the user from the request body
        const { digit1, digit2, digit3, digit4, digit5, digit6 } = req.body;
        const enteredVerificationCode = `${digit1}${digit2}${digit3}${digit4}${digit5}${digit6}`;

        // Find the recruiter in the database based on the provided verification code
        const recruiter = await Recruiter.findOne({ verificationCode: enteredVerificationCode });

        // Check if the recruiter exists and if the entered verification code matches the one stored in the database
        if (!recruiter) {
            return res.render("error", { message: "Invalid verification code." });
        }

        // If verification is successful, update the 'is_verified' field to 1
        await Recruiter.updateOne({ _id: recruiter._id }, { $set: { is_verified: 1 } });

        // Redirect the user to the login page or any other desired page
        res.redirect("/recruiter_login");
    } catch (error) {
        console.error("Error occurred while verifying email:", error);
        res.status(500).send("Internal Server Error.");
    }
};

app.post("/verify", verifyMail);


app.post("/email_verfied", verifyMail);
app.get("/main", (req, res) => {

    // Apprach 1
    // exec('python run.py', (error, stdout, stderr) => {
    //     if (error) {
    //         console.error(`Error executing Python script: ${error}`);
    //         return res.status(500).send('An error occurred while executing the Python script');
    //     }
    //     // Handle success case
    //     console.log(`Python script output: ${stdout}`);
    //     res.send(stdout); // Send the output of the Python script as response
    // });

    // Approach 2
    const email = req.session.email;
    if (!email) {
        return res.send("Email not found in session");
    }
    res.redirect(`http://127.0.0.1:5000/main?email=${email}`);
});


app.post("/signup", async (req, res) => {
    const data = {
        email: req.body.email,
        password: req.body.password,
        confirmPassword: req.body.confirmPassword,
        interests: [] ,
        setup:0,
    };
    try {
        const newUser = new User(data);
        await newUser.save();
        res.render("login");
    } catch (error) {
        console.error("Error occurred while signing up:", error);
        res.status(500).send("Internal Server Error.");
    }
});
app.post("/login", async (req, res) => {
    try {
        const user = await User.findOne({ email: req.body.email });

        if (!user || user.password !== req.body.password) {
            return res.send("Invalid email or password.");
        }

        req.session.email = req.body.email; 

        if (user.setup === 0) {
         
            return res.redirect("/question");
        } else {
         
            return res.redirect("/main");
        }
    } catch (error) {
        console.error("Error occurred while logging in:", error);
        res.status(500).send("Internal Server Error.");
    }
});

const sendVerifyEmail = async (workemail, verificationCode) => {
    try {
        const transporter = nodemailer.createTransport({
            host: 'smtp.gmail.com',
            port: 587,
            secure: false,
            requireTLS: true,
            auth: {
                user: 'shreyaspawaskar2@gmail.com',
                pass: 'rxipseckzrwynmss'
            }
        });

        const mailoptions = {
            from: 'shreyaspawaskar2@gmail.com',
            to: workemail,
            subject: 'Verify your account on GuideSphere',
            html: `<p>Dear Recruiter,</p>
            <p>Thank you for choosing GuideSphere to streamline your recruitment process. This verfication process is to confirm your email address and register you as a verfied recruiter.</p>
            <p>Please find your One-Time-Password(OTP) below:</p>
            <p>OTP:  <strong> ${verificationCode} </strong></p>
            <p>Kindly enter this OTP in the designated field on our website to complete registration process.</p>
            <br>
            <p>If not done by you, Kindly discard this email</p>
            
            <br>
            <p>Best regards,</p>
            <strong>GuideSphere</strong>`
        };

        transporter.sendMail(mailoptions, function (error, info) {
            if (error) {
                console.log(error);
            } else {
                console.log("Email has been sent:", info.response);
            }
        });
    } catch (error) {
        console.log(error.message);
    }
};

const generateVerificationCode = () => {
    // Generate a random 6-digit code
    return Math.floor(100000 + Math.random() * 900000);
};
app.post("/recruiter_signup", async (req, res) => {
    const data = {
        workemail: req.body.workemail,
        password: req.body.password,
        contactno: req.body.contactno,
        companyname: req.body.companyname,
        companylocation: req.body.companylocation,
        companysize: req.body.companysize,
        is_verified: 0, // Initialize is_verified as 0
        verificationCode: null,
        jobs: [] ,
    };

    try {
        // Generate verification code
        const verificationCode = generateVerificationCode();

        // Store the verification code in the session
        req.session.verificationCode = verificationCode;

        // Store the verification code in the database
        data.verificationCode = verificationCode;

        // Create a new Recruiter instance with the data
        const newRecruiter = new Recruiter(data);

        // Save the new recruiter with verification code
        await newRecruiter.save();
        
        // Send verification email
        sendVerifyEmail(req.body.workemail, verificationCode);

        // Render email_verified template
        res.render("email_verfied");
    } catch (error) {
        console.error("Error occurred while signing up:", error);
        res.status(500).send("Internal Server Error.");
    }
});



app.post("/recruiter_login", async (req, res) => {
    try {
        const recruiter = await Recruiter.findOne({ workemail: req.body.workemail });

        if (!recruiter || recruiter.password !== req.body.password) {
            return res.send("Invalid email or password.");
        }
        
         // Set workemail and companyname in session
         req.session.workemail = req.body.workemail;
         req.session.companyname = recruiter.companyname;
 

        // Redirect to jobpost page
        res.redirect(`/jobpost`);
    } catch (error) {
        console.error("Error occurred while logging in:", error);
        res.status(500).send("Internal Server Error.");
    }
});




app.listen(3000, () => {
    console.log("Port connected");
});