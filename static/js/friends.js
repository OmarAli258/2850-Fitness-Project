//search system for finding users to add as friends, similar to the dashboard search but for users instead of activites
const friendSearchInput = document.getElementById("friendSearchInput");
const friendSearchResults = document.getElementById("friendSearchResults");
let friendSearchTimer = null; //delays the search so its not firing on every letter typed

if (friendSearchInput) {
    friendSearchInput.addEventListener("input", function () { //runs when user types in the boxx
        const query = friendSearchInput.value.trim();
        clearTimeout(friendSearchTimer); //cancels any pending search

        if (query === "") { //hide dropdown if empty
            friendSearchResults.classList.remove("active");
            return;
        }

        //wait 0.25s after typing stops before actually searching
        friendSearchTimer = setTimeout(function () {
            fetchUserResults(query);
        }, 250);
    });

    //hide dropdown if user clicks outside the search area
    document.addEventListener("click", function (event) {
        if (!event.target.closest(".search-wrapper")) {
            friendSearchResults.classList.remove("active");
        }
    });
}

//calls the flask api to search for users by name
function fetchUserResults(query) {
    fetch("/api/users/search?q=" + encodeURIComponent(query))
        .then(function (response) {
            return response.json();
        })
        .then(function (results) {
            renderUserResults(results);
        })
        .catch(function (error) {
            console.error("Search failed:", error);
        });
}

//builds the dropdown showing each matching user with a send eequest button
function renderUserResults(results) {
    if (results.length === 0) {
        friendSearchResults.innerHTML = '<div class="search-empty">No users found</div>';
        friendSearchResults.classList.add("active");
        return;
    }

    let html = "";
    //loop through all the users and create a clickable card with a send request button
    for (const user of results) {
        let actionHtml = `
            <form method="POST" action="/friends/request/${user.id}" style="margin-top: 0.5rem;">
                <button type="submit" class="btn btna" style="padding: 0.4rem 1rem; font-size: 0.85rem;">Send Request</button>
            </form>
        `;

        if (user.friendship_status === "friends") {
            actionHtml = '<div class="search-result-meta" style="margin-top: 0.5rem; color: var(--yellow); font-weight: 700;">Already friends</div>';
        } else if (user.friendship_status === "request_sent") {
            actionHtml = '<div class="search-result-meta" style="margin-top: 0.5rem; color: var(--text-muted); font-weight: 700;">Request sent</div>';
        } else if (user.friendship_status === "request_received") {
            actionHtml = '<div class="search-result-meta" style="margin-top: 0.5rem; color: var(--text-muted); font-weight: 700;">Respond in pending requests</div>';
        }

        html += `
            <div class="search-result">
                <div class="search-result-type">${user.name}</div>
                <div class="search-result-meta">${user.email}</div>
                ${actionHtml}
            </div>
        `;
    }

    friendSearchResults.innerHTML = html;
    friendSearchResults.classList.add("active");
}
