const friendSearchInput = document.getElementById("friendSearchInput");
const friendSearchResults = document.getElementById("friendSearchResults");
let friendSearchTimer = null;

if (friendSearchInput) {
    friendSearchInput.addEventListener("input", function () {
        const query = friendSearchInput.value.trim();
        clearTimeout(friendSearchTimer);

        if (query === "") {
            friendSearchResults.classList.remove("active");
            return;
        }

        friendSearchTimer = setTimeout(function () {
            fetchUserResults(query);
        }, 250);
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".search-wrapper")) {
            friendSearchResults.classList.remove("active");
        }
    });
}

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

function renderUserResults(results) {
    if (results.length === 0) {
        friendSearchResults.innerHTML = '<div class="search-empty">No users found</div>';
        friendSearchResults.classList.add("active");
        return;
    }

    let html = "";
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
