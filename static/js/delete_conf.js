        let targetId = null;
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', function() {
                targetId = this.getAttribute('data-id');
                const name = this.getAttribute('data-name');

                document.getElementById('itemNameToDelete').textContent = name;
                deleteModal.show();
            });
        });

        document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
            if (!targetId) return;

            fetch(`/recipe/${targetId}/delete`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = data.redirect_url;
                } else {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.location.reload();
            })
            .finally(() => {
                deleteModal.hide();
            });
        });