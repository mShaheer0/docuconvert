function formatSize(bytes) {
    if (bytes === 0) return "0 B";
    const units = ["B", "KB", "MB", "GB"];
    let value = bytes;
    let index = 0;

    while (value >= 1024 && index < units.length - 1) {
        value /= 1024;
        index += 1;
    }

    return `${value.toFixed(2)} ${units[index]}`;
}

function setStatus({ statusEl, type, message }) {
    statusEl.className = `status ${type} visible`;
    statusEl.textContent = message;
}

function clearStatus(statusEl) {
    statusEl.className = "status";
    statusEl.textContent = "";
}

function resolveApiUrl(endpoint) {
    if (typeof buildApiUrl === "function") {
        return buildApiUrl(endpoint);
    }
    return endpoint;
}

function getFilenameFromDisposition(disposition) {
    if (!disposition) return null;

    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match?.[1]) {
        return decodeURIComponent(utf8Match[1]);
    }

    const quotedMatch = disposition.match(/filename="([^"]+)"/i);
    if (quotedMatch?.[1]) {
        return quotedMatch[1];
    }

    const plainMatch = disposition.match(/filename=([^;]+)/i);
    if (plainMatch?.[1]) {
        return plainMatch[1].trim().replace(/^"|"$/g, "");
    }

    return null;
}

function initConverter(config) {
    const {
        formId,
        dropZoneId,
        fileInputId,
        previewId,
        convertButtonId,
        resetButtonId,
        statusId,
        progressTrackId,
        endpoint,
        accept,
        expectedMimeType = "application/pdf",
    } = config;

    const form = document.getElementById(formId);
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(fileInputId);
    const preview = document.getElementById(previewId);
    const convertButton = document.getElementById(convertButtonId);
    const resetButton = document.getElementById(resetButtonId);
    const statusEl = document.getElementById(statusId);
    const progressTrack = document.getElementById(progressTrackId);

    let selectedFile = null;

    const showPreview = (file) => {
        preview.classList.add("visible");
        preview.innerHTML = `Name: ${file.name}<br>Size: ${formatSize(file.size)}`;
    };

    const hidePreview = () => {
        preview.classList.remove("visible");
        preview.innerHTML = "";
    };

    const resetState = () => {
        selectedFile = null;
        fileInput.value = "";
        hidePreview();
        clearStatus(statusEl);
        convertButton.disabled = true;
        progressTrack.classList.remove("visible");
    };

    const setFile = (file) => {
        if (!file) return;

        const extension = file.name.split(".").pop()?.toLowerCase() || "";
        const acceptedExtensions = accept.replaceAll(".", "").split(",");

        if (!acceptedExtensions.includes(extension)) {
            setStatus({
                statusEl,
                type: "error",
                message: `Only ${accept} files are supported on this page.`,
            });
            return;
        }

        selectedFile = file;
        showPreview(file);
        clearStatus(statusEl);
        convertButton.disabled = false;
    };

    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", (event) => {
        const file = event.target.files?.[0];
        setFile(file);
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropZone.parentElement.classList.add("drag-over");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            event.stopPropagation();
            dropZone.parentElement.classList.remove("drag-over");
        });
    });

    dropZone.addEventListener("drop", (event) => {
        const file = event.dataTransfer?.files?.[0];
        setFile(file);
    });

    resetButton.addEventListener("click", resetState);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!selectedFile) {
            setStatus({
                statusEl,
                type: "error",
                message: "Select a file first.",
            });
            return;
        }

        convertButton.disabled = true;
        progressTrack.classList.add("visible");
        setStatus({
            statusEl,
            type: "success",
            message: "Converting your file...",
        });

        try {
            const formData = new FormData();
            formData.append("uploaded_file", selectedFile);

            const response = await fetch(resolveApiUrl(endpoint), {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: "Conversion failed." }));
                throw new Error(errorData.detail || "Conversion failed.");
            }

            const blob = await response.blob();
            const disposition = response.headers.get("Content-Disposition") || "";
            const contentType = response.headers.get("Content-Type") || "";

            if (!contentType.toLowerCase().includes(expectedMimeType) || blob.size === 0) {
                const maybeText = await blob.text().catch(() => "Conversion failed.");
                throw new Error(maybeText || "Conversion failed. Output file was not produced.");
            }

            const outputFilename = getFilenameFromDisposition(disposition) || "converted.pdf";

            const downloadUrl = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = downloadUrl;
            link.download = outputFilename;
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(downloadUrl);

            setStatus({
                statusEl,
                type: "success",
                message: "Conversion completed. Your download should start automatically.",
            });
        } catch (error) {
            setStatus({
                statusEl,
                type: "error",
                message: error.message || "Conversion failed. Please try again.",
            });
        } finally {
            progressTrack.classList.remove("visible");
            convertButton.disabled = false;
        }
    });

    resetState();
}
