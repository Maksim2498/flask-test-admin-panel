async function fetchAndReload(url, method = "GET") {
    await fetch(url, { method })
    location.reload()
}
