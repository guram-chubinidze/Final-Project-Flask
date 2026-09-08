
const quill = new Quill('#full-recipe', {
  modules: {
    toolbar: true,
  },
  placeholder: 'Compose an epic...',
  theme: 'snow', // or 'bubble'
});

 // Intercept form submission to populate the hidden input
        const form = document.getElementById('post-form');
        form.onsubmit = function() {
            // Get the HTML content from the editor
            const content = quill.getSemanticHTML(); 
            console.log(content);
            // Populate the hidden field
            document.getElementById('full_recipe').value = content;
        };