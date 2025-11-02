async function fetchData() {
    const response = await fetch('/api/community_projects/');
    const data = await response.json();
    addItems(data);
}

// Function to add items to the DOM
function addItems(items) {
    const itemList = document.getElementById('community-project-container');
    itemList.innerText = "";
    items.forEach(item => {
        console.log(item)
        const onclick_project = "window.open('https://scratch.mit.edu/projects/"+item.project_id.toString()+"/', '_blank');"
        const onclick_author = "window.open('https://scratch.mit.edu/users/"+item.author.toString()+"/', '_blank');"
        const new_element = '<div style="cursor: pointer" onclick="'+onclick_project+'" class="project"><img src="'+item.thumbnail_url+'" alt="Project Thumbnail" class="project-thumbnail"><h3 style="cursor: pointer; margin: 7px;" onclick="'+onclick_project+'" class="project-name">'+item.title+'</h3><p style="cursor: pointer;" class="project-author" onclick="'+onclick_author+'">by '+item.author+'</p></div>'
        itemList.innerHTML += new_element;
    });
}

// Fetch data when the page loads
window.onload = fetchData;