const expenseDate = document.getElementById("expense-date");

if (expenseDate) {
    const today = new Date();

    const year = today.getFullYear();

    const month = String(
        today.getMonth() + 1
    ).padStart(2, "0");

    const day = String(
        today.getDate()
    ).padStart(2, "0");

    if (!expenseDate.value) {
        expenseDate.value =
            `${year}-${month}-${day}`;
    }
}


/* =========================================
   SPLIT EXPENSE
========================================= */

const splitOptions = document.querySelectorAll(
    'input[name="split_type"]'
);

const exceptMembers =
    document.getElementById("except-members");

if (exceptMembers) {

    function updateExcludedMembersVisibility() {
        const exceptSelected =
            document.querySelector('input[name="split_type"][value="except"]:checked');

        exceptMembers.style.display =
            exceptSelected ? "block" : "none";
    }

    splitOptions.forEach(function (option) {

        option.addEventListener(
            "change",
            function () {

                updateExcludedMembersVisibility();

            }
        );

    });

    updateExcludedMembersVisibility();

}


/* =========================================
   LAST OPENED TRIP
========================================= */

const currentTripId =
    window.location.pathname.match(
        /\/trip\/(\d+)/
    );

if (currentTripId) {

    localStorage.setItem(
        "lastOpenedTrip",
        currentTripId[1]
    );

}


/* =========================================
   FLOATING ADD EXPENSE
========================================= */

const floatingExpenseButton =
    document.querySelector(
        ".floating-expense-btn"
    );

if (floatingExpenseButton) {

    const lastTripId =
        localStorage.getItem(
            "lastOpenedTrip"
        );

    if (lastTripId) {

        floatingExpenseButton.href =
            `/manage-expenses/${lastTripId}`;

    }

}


/* =========================================
   CHANGE TRIP
========================================= */

const changeTrip =
    document.getElementById("change-trip");

if (changeTrip) {

    changeTrip.addEventListener(
        "change",
        function () {

            const selectedTripId =
                this.value;

            if (selectedTripId) {

                localStorage.setItem(
                    "lastOpenedTrip",
                    selectedTripId
                );

                window.location.href =
                    "/manage-expenses/" +
                    selectedTripId;

            }

        }
    );

}


/* =========================================
   TRIP MEMORY PHOTO SELECTION
========================================= */

const tripPhotos =
    document.getElementById("trip-photos");

const photoCount =
    document.getElementById("photo-count");

const photoPreview =
    document.getElementById("photo-preview");

const photoError =
    document.getElementById("photo-error");

const startMemoryButton =
    document.getElementById(
        "start-memory-btn"
    );


if (
    tripPhotos &&
    photoCount &&
    photoPreview &&
    photoError &&
    startMemoryButton
) {

    /* PHOTO SELECTION */

    tripPhotos.addEventListener(
        "change",
        function () {

            const files =
                Array.from(
                    tripPhotos.files
                );

            photoPreview.innerHTML = "";

            photoError.textContent = "";

            photoCount.textContent =
                `${files.length} photos selected`;


            if (files.length < 5) {

                startMemoryButton.disabled =
                    true;

                photoError.textContent =
                    "Please select at least 5 photos.";

            } else {

                startMemoryButton.disabled =
                    false;

                photoError.textContent =
                    `${files.length} photos ready for your memory.`;

            }


            /* PHOTO PREVIEWS */

            files.forEach(
                function (file) {

                    const image =
                        document.createElement(
                            "img"
                        );

                    image.src =
                        URL.createObjectURL(
                            file
                        );

                    image.alt =
                        "Trip memory photo";

                    photoPreview.appendChild(
                        image
                    );

                }
            );

        }
    );


    /* START MEMORY */

    startMemoryButton.addEventListener(
        "click",
        function () {

            const files =
                Array.from(
                    tripPhotos.files
                );


            if (files.length < 5) {

                photoError.textContent =
                    "Please select at least 5 photos.";

                return;

            }


            const readers =
                files.map(
                    function (file) {

                        return new Promise(
                            function (
                                resolve,
                                reject
                            ) {

                                const reader =
                                    new FileReader();


                                reader.onload =
                                    function () {

                                        resolve(
                                            reader.result
                                        );

                                    };


                                reader.onerror =
                                    function () {

                                        reject(
                                            reader.error
                                        );

                                    };


                                reader.readAsDataURL(
                                    file
                                );

                            }
                        );

                    }
                );


            startMemoryButton.disabled =
                true;

            startMemoryButton.textContent =
                "Preparing Memory...";


            Promise.all(readers)
                .then(
                    function (photoData) {

                        sessionStorage.setItem(
                            "tripMemoryPhotos",
                            JSON.stringify(
                                photoData
                            )
                        );


                        if (
                            typeof tripMemoryUrl !==
                            "undefined"
                        ) {

                            window.location.href =
                                tripMemoryUrl;

                        } else {

                            photoError.textContent =
                                "Memory page URL is missing.";

                            startMemoryButton.disabled =
                                false;

                            startMemoryButton.textContent =
                                "✨ Start Memory";

                        }

                    }
                )
                .catch(
                    function () {

                        photoError.textContent =
                            "Something went wrong while loading the photos.";

                        startMemoryButton.disabled =
                            false;

                        startMemoryButton.textContent =
                            "✨ Start Memory";

                    }
                );

        }
    );

}


/* =========================================
   30 SECOND MEMORY EXPERIENCE
========================================= */

const memoryPhotoContainer =
    document.getElementById(
        "memory-photo-container"
    );

const memoryTitle =
    document.getElementById(
        "memory-title"
    );

const memoryMessage =
    document.getElementById(
        "memory-message"
    );

const memorySmallText =
    document.getElementById(
        "memory-small-text"
    );

const memoryProgressBar =
    document.getElementById(
        "memory-progress-bar"
    );

const memoryFinal =
    document.getElementById(
        "memory-final"
    );

const memoryMusic =
    document.getElementById(
        "memory-music"
    );


if (
    memoryPhotoContainer &&
    memoryTitle &&
    memoryMessage &&
    memorySmallText &&
    memoryProgressBar &&
    memoryFinal
) {

    const savedPhotos =
        sessionStorage.getItem(
            "tripMemoryPhotos"
        );


    if (savedPhotos) {

        const photos =
            JSON.parse(savedPhotos);


        if (photos.length >= 5) {

            startMemoryExperience(
                photos
            );

        }

    }


    function startMemoryExperience(photos) {

        /* START BACKGROUND MUSIC */

        if (memoryMusic) {

            memoryMusic.currentTime = 0;

            memoryMusic.play().catch(
                function () {}
            );

        }


        memoryFinal.style.display =
            "none";


        memoryPhotoContainer.innerHTML =
            "";


        const totalDuration =
            30000;


        const photoDuration =
            totalDuration / photos.length;


        let currentPhoto = 0;


        function showPhoto(index) {

            if (index >= photos.length) {

                finishMemory();

                return;

            }


            const image =
                document.createElement("img");


            image.src =
                photos[index];


            image.className =
                "memory-photo";


            memoryPhotoContainer
                .appendChild(image);


            setTimeout(function () {

                image.classList.add(
                    "memory-photo-visible"
                );

            }, 50);


            updateMemoryText(index);


            const progress =
                (
                    (index + 1) /
                    photos.length
                ) * 100;


            memoryProgressBar.style.width =
                `${progress}%`;


            setTimeout(function () {

                image.classList.remove(
                    "memory-photo-visible"
                );


                image.classList.add(
                    "memory-photo-exit"
                );


                setTimeout(function () {

                    image.remove();

                    currentPhoto++;

                    showPhoto(
                        currentPhoto
                    );

                }, 700);

            }, photoDuration - 700);

        }


        function updateMemoryText(index) {

            const messages = [

                {
                    small: "THE JOURNEY BEGINS",

                    title: "It started with a plan...",

                    message:
                        "Aur phir ek safar shuru hua."
                },

                {
                    small: "THE ROAD",

                    title: "Miles became memories.",

                    message:
                        "Har raasta apni ek kahani chhod gaya."
                },

                {
                    small: "TOGETHER",

                    title: "The best moments were shared.",

                    message:
                        "Kyuki achhe pal tab aur khoobsurat ho jaate hain jab apne saath ho."
                },

                {
                    small: "THE MOMENTS",

                    title: "Some moments stay forever.",

                    message:
                        "Kuch pal camera mein capture hote hain, kuch dil mein."
                },

                {
                    small: "THE MEMORIES",

                    title: "And now...",

                    message:
                        "Ye safar ek yaad ban chuka hai."
                }

            ];


            const message =
                messages[
                    index %
                    messages.length
                ];


            memorySmallText.textContent =
                message.small;


            memoryTitle.textContent =
                message.title;


            memoryMessage.textContent =
                message.message;


            memorySmallText
                .classList.remove(
                    "memory-text-change"
                );


            memoryTitle
                .classList.remove(
                    "memory-text-change"
                );


            memoryMessage
                .classList.remove(
                    "memory-text-change"
                );


            setTimeout(function () {

                memorySmallText
                    .classList.add(
                        "memory-text-change"
                    );


                memoryTitle
                    .classList.add(
                        "memory-text-change"
                    );


                memoryMessage
                    .classList.add(
                        "memory-text-change"
                    );

            }, 50);

        }


        function finishMemory() {

            /* STOP BACKGROUND MUSIC */

            if (memoryMusic) {

                memoryMusic.pause();

                memoryMusic.currentTime = 0;

            }


            memoryPhotoContainer
                .classList.add(
                    "memory-fade-out"
                );


            memoryProgressBar.style.width =
                "100%";


            setTimeout(function () {

                memoryPhotoContainer.innerHTML =
                    "";


                memoryFinal.style.display =
                    "flex";


                memoryFinal.classList.add(
                    "memory-final-visible"
                );

            }, 1200);

        }


        showPhoto(currentPhoto);

    }

}

/* =========================================
   COPY TRIP CODE
========================================= */

const copyTripCodeButton =
    document.getElementById("copy-trip-code");

const tripCodeElement =
    document.getElementById("trip-code");

if (
    copyTripCodeButton &&
    tripCodeElement
) {

    copyTripCodeButton.addEventListener(
        "click",
        function () {

            const tripCode =
                tripCodeElement.textContent.trim();

            navigator.clipboard.writeText(
                tripCode
            );

            copyTripCodeButton.textContent =
                "✓ Copied";

            setTimeout(function () {

                copyTripCodeButton.textContent =
                    "📋 Copy";

            }, 1500);

        }
    );

}

/* =========================================
   PWA SERVICE WORKER
========================================= */

if ("serviceWorker" in navigator) {

    window.addEventListener("load", function () {

        navigator.serviceWorker
            .register("/static/service-worker.js")
            .then(function () {
                console.log("Service Worker registered successfully.");
            })
            .catch(function (error) {
                console.error(
                    "Service Worker registration failed:",
                    error
                );
            });

    });

}