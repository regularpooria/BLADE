# Prerequisites
1. You need to have a SSH client installed, it is preferred that you are using a UNIX client (MacOS, Linux or WSL2[^1])
2. You need an active DRA account, It can be obtained through your sponsor (usually a professor)
3. Some knowledge of UNIX systems and how to navigate through their filesystem
---

## About the clusters
There are 4 clusters in total that are active right now, each have their own capabilities and are suited for their respective tasks:
1. [Beluga](https://docs.alliancecan.ca/wiki/B%C3%A9luga/en) (**This is the one we'll be using**)
2. [Cedar](https://docs.alliancecan.ca/wiki/Cedar)
3. [Narval](https://docs.alliancecan.ca/wiki/Graham)
4. [Graham](https://docs.alliancecan.ca/wiki/Narval/en)\
They all have GPUs but some have more CPUs which make them better for CPU heavy jobs, checkout the links on each to see what specific hardware they have

---

## Step 1: Enroll in Duo MFA (Required)

All users must set up Duo 2FA before SSH access.

1. Go to: [https://mfa.computecanada.ca](https://mfa.computecanada.ca)  
2. Log in with your Alliance credentials.
3. Register your mobile device with **Duo Mobile** or phone/SMS.

4. Test login to a cluster:
```bash
ssh your_username@beluga.alliancecan.ca
```

---

## Step 2: Check If You Already Have an SSH Key

Check if an SSH key already exists on your machine:

```bash
ls ~/.ssh/id_rsa.pub
```

- If it exists, skip to **Step 4**.
- If not, continue to Step 3.

---

## Step 3: Generate a New SSH Key

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

- Make sure to change the email to the email you're using for your DRA account
- Accept default location (`~/.ssh/id_rsa`)
- Choose a passphrase.

---

## Step 4: Upload SSH Key to a Cluster

Copy with `ssh-copy-id`:
```bash
ssh-copy-id your_username@beluga.alliancecan.ca
```

---


[^1]: If you are using WSL2, please make sure that you have set up systemd properly and that you can access it, it's a nice to have.