// Function to handle the entry of observed elements
function handleIntersection(entries) {
    entries.forEach(entry => {
        if (!entry.isIntersecting) {
            var elements = document.getElementsByClassName("header-btn");
            for (let i = 0; i < elements.length; i++) {
                const element = elements[i];
                element.classList.add('fly-in'); // Add the fly-in class to trigger the animation
                observer.unobserve(element); // Stop observing once the animation has triggered
            }
            var elements = document.getElementsByClassName("logo-section");
            for (let i = 0; i < elements.length; i++) {
                const element = elements[i];
                element.classList.add('fly-in'); // Add the fly-in class to trigger the animation
                observer.unobserve(element); // Stop observing once the animation has triggered
            }
        }
    });
}

// Options for the Intersection Observer
const options = {
    root: null, // Use the viewport as the root
    rootMargin: '0px', // No margin
    threshold: 0.1 // Trigger when 10% of the element is in view
};

// Create an Intersection Observer instance
const observer = new IntersectionObserver(handleIntersection, options);

// Select elements to observe
const flyInElements = document.querySelectorAll('.section-1'); // Adjust selectors as needed

// Observe each element
flyInElements.forEach(element => {
    observer.observe(element);
});

// Function to handle the entry of the expanding box
function handleBoxIntersection(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            var box = entry.target;
            boxObserver.unobserve(box); // Stop observing once the animation has triggered

            // Add a wait time (e.g., 500ms) before opening the box
            setTimeout(() => {
                const width = box.dataset.width; // Assuming it's a string (like '400px' or '50%')
                box.style.width = width
                box.classList.add('open'); // Add class to trigger the expansion
                if (width) {
                    box.style.width = width; // Set the width dynamically
                }
    
                function handleTextBox(query) {
                    var textBox = box.querySelector(query);
                    const text = textBox.dataset.text; // Store the original text
                    textBox.textContent = ""; // Clear the box for typing effect
                    let index = 0;

                    // Function to type text slowly
                    function type() {
                        if (index < text.length) {
                            textBox.textContent += text.charAt(index); // Append the current character
                            index++;
                            setTimeout(type, 50); // Schedule the next character typing
                        } else {
                            isTyping = false; // Reset flag when typing is done
                        }
                    }

                    type(); // Start typing the text
                }
                for (let i = 0; i <= box.children.length; i++) {
                    handleTextBox("#expandText"+i.toString());
                }

            }, 200); // Adjust this value to set the wait time (in milliseconds)

        }
    });
}

// Create an Intersection Observer instance for the expanding box
const boxObserver = new IntersectionObserver(handleBoxIntersection, {
    root: null, // Use the viewport as the root
    rootMargin: '0px', // No margin
    threshold: 0.1 // Trigger when 10% of the element is in view
});

// Observe the expanding boxes
boxObserver.observe(document.getElementById('pipInstallCmd'));
boxObserver.observe(document.getElementById('pyImportCmd'));
boxObserver.observe(document.getElementById('logInCmd'));
boxObserver.observe(document.getElementById('cloudCmd'));
boxObserver.observe(document.getElementById('siteCmd'));
