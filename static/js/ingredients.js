document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('ingredients-container');
    const addButton = document.getElementById('add-ingredient');

    // ინგრედიენტის დამატება
    addButton.addEventListener('click', function () {
        const rowCount = container.getElementsByClassName('ingredient-row').length;
        
        // ვქმნით ახალ რიგს ზუსტად იმავე კლასებით და ნომინაციით (index-ით)
        const newRow = document.createElement('div');
        newRow.className = 'row g-2 mb-2 ingredient-row align-items-end';
        newRow.innerHTML = `
            <div class="col-md-7">
                <input class="form-control" id="ingredients-${rowCount}-name" name="ingredients-${rowCount}-name" placeholder="e.g. Flour" type="text" value="">
            </div>
            <div class="col-md-4">
                <input class="form-control" id="ingredients-${rowCount}-amount" name="ingredients-${rowCount}-amount" placeholder="e.g. 500g" type="text" value="">
            </div>
            <div class="col-md-1 d-flex align-items-center">
                <button type="button" class="btn btn-outline-danger btn-sm w-100 remove-ing" title="Remove">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        `;
        container.appendChild(newRow);
    });

    // ინგრედიენტის წაშლა (Event Delegation)
    container.addEventListener('click', function (e) {
        if (e.target.closest('.remove-ing')) {
            const row = e.target.closest('.ingredient-row');
            // დავტოვოთ მინიმუმ 1 ველი რომ სრულიად არ დაიცარიელოს
            if (container.getElementsByClassName('ingredient-row').length > 1) {
                row.remove();
            } else {
                // თუ ბოლო ველვია, უბრალოდ გავასუფთავოთ შიგთავსი
                row.querySelectorAll('input').forEach(input => input.value = '');
            }
        }
    });
});

