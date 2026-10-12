
const form = document.getElementById("certificateForm");
const recipientList = document.getElementById("recipientList");
const addRecipientButton = document.getElementById("addRecipient");
const generateButton = document.getElementById("generateButton");
const message = document.getElementById("message");

let latestJobId = null;
let pollingTimer = null;

function addRecipient(name = "", email = "") {
    if (recipientList.children.length >= 1000) {
        showMessage("You can add a maximum of 1,000 recipients.", true);
        return;
    }

    const row = document.createElement("div");
    row.className = "recipient-row";

    const nameLabel = document.createElement("label");
    nameLabel.textContent = "Recipient name";

    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.name = "recipientName";
    nameInput.placeholder = "Full name";
    nameInput.required = true;
    nameInput.maxLength = 200;
    nameInput.value = name;

    const emailLabel = document.createElement("label");
    emailLabel.textContent = "Email address";

    const emailInput = document.createElement("input");
    emailInput.type = "email";
    emailInput.name = "recipientEmail";
    emailInput.placeholder = "name@example.com";
    emailInput.required = true;
    emailInput.maxLength = 320;
    emailInput.value = email;

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-recipient";
    removeButton.textContent = "×";
    removeButton.setAttribute("aria-label", "Remove recipient");

    removeButton.addEventListener("click", () => {
        row.remove();

        if (recipientList.children.length === 0) {
            addRecipient();
        }
    });

    nameLabel.appendChild(nameInput);
    emailLabel.appendChild(emailInput);

    row.append(nameLabel, emailLabel, removeButton);
    recipientList.appendChild(row);
}

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = isError ? "error" : "success";
}

function setStatus(status) {
    const element = document.getElementById("jobStatus");
    element.textContent = status.replaceAll("_", " ");
    element.className = "status-label";

    if (status === "COMPLETED") {
        element.classList.add("complete");
    } else if (status === "COMPLETED_WITH_ERRORS" || status === "FAILED") {
        element.classList.add("failed");
    }
}

addRecipientButton.addEventListener("click", () => addRecipient());

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const recipients = [...recipientList.querySelectorAll(".recipient-row")].map(
        (row) => ({
            name: row.querySelector('[name="recipientName"]').value.trim(),
            email: row.querySelector('[name="recipientEmail"]').value.trim(),
        })
    );

    if (recipients.length === 0) {
        showMessage("Please add at least one recipient.", true);
        return;
    }

    if (pollingTimer) {
        clearTimeout(pollingTimer);
        pollingTimer = null;
    }

    const payload = {
        event_name: document.getElementById("eventName").value.trim(),
        issuer: document.getElementById("issuer").value.trim(),
        recipients,
    };

    generateButton.disabled = true;
    generateButton.textContent = "Submitting...";
    showMessage("Submitting your certificate generation job...");

    try {
        const response = await fetch("/api/jobs/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail
                    ? (typeof data.detail === "string"
                        ? data.detail
                        : JSON.stringify(data.detail))
                    : "Could not create the job."
            );
        }

        latestJobId = data.job_id;
        showMessage(`Job created successfully: ${latestJobId}`);
        setStatus(data.status);
        document.getElementById("jobInfo").textContent =
            `Job ID: ${latestJobId} · ${payload.event_name}`;

        await refreshJob(latestJobId);
    } catch (error) {
        showMessage(error.message || "Something went wrong.", true);
        setStatus("FAILED");
    } finally {
        generateButton.disabled = false;
        generateButton.textContent = "Generate certificates →";
    }
});

async function refreshJob(jobId) {
    try {
        const response = await fetch(`/api/jobs/${encodeURIComponent(jobId)}`);

        if (!response.ok) {
            throw new Error("Unable to retrieve job status.");
        }

        const job = await response.json();

        document.getElementById("totalCount").textContent = job.total_count;
        document.getElementById("successCount").textContent = job.success_count;
        document.getElementById("failedCount").textContent = job.failed_count;

        setStatus(job.status);
        renderRecipients(job.recipients);

        if (job.status === "COMPLETED" || job.status === "COMPLETED_WITH_ERRORS") {
            showMessage(
                `Finished! ${job.success_count} successful, ${job.failed_count} failed.`
            );
            return;
        }

        if (job.status === "FAILED") {
            showMessage("The generation job failed.", true);
            return;
        }

        pollingTimer = setTimeout(() => refreshJob(jobId), 1500);
    } catch (error) {
        showMessage(error.message || "Could not refresh job status.", true);
    }
}

function renderRecipients(recipients) {
    const body = document.getElementById("resultsBody");
    body.replaceChildren();

    if (!recipients || recipients.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        cell.colSpan = 4;
        cell.className = "empty";
        cell.textContent = "No recipient results available.";
        row.appendChild(cell);
        body.appendChild(row);
        return;
    }

    recipients.forEach((recipient) => {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.textContent = recipient.name;

        const emailCell = document.createElement("td");
        emailCell.textContent = recipient.email || "—";

        const statusCell = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = "badge";

        if (recipient.status === "COMPLETED") {
            badge.classList.add("completed");
        } else if (recipient.status === "FAILED") {
            badge.classList.add("failed");
        }

        badge.textContent = recipient.status;
        statusCell.appendChild(badge);

        const downloadCell = document.createElement("td");

        if (recipient.download_url && recipient.status === "COMPLETED") {
            const link = document.createElement("a");
            link.className = "download-link";
            link.href = recipient.download_url;
            link.textContent = "↓ Download PDF";
            link.setAttribute("download", "");
            downloadCell.appendChild(link);
        } else if (recipient.status === "FAILED") {
            downloadCell.textContent = recipient.error || "Generation failed";
        } else {
            downloadCell.textContent = "Preparing...";
        }

        row.append(nameCell, emailCell, statusCell, downloadCell);
        body.appendChild(row);
    });
}

// Show one recipient row when the page first opens.
addRecipient();
