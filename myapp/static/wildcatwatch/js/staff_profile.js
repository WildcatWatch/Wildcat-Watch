document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profile-form');
    const display = document.getElementById('profile-display');
    const dobInput = form.querySelector('[name="dob"]');
    const ageInput = form.querySelector('[name="age"]');

    // --- Auto-calculate age from DOB ---
    dobInput.addEventListener('change', function() {
        if (dobInput.value) {
            const dob = new Date(dobInput.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const m = today.getMonth() - dob.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
            ageInput.value = age;
        } else {
            ageInput.value = '';
        }
    });

    // --- Toggle edit/display ---
    window.toggleEdit = function() {
        if (form.style.display === 'none' || form.style.display === '') {
            form.style.display = 'block';
            display.style.display = 'none';
        } else {
            form.style.display = 'none';
            display.style.display = 'block';
        }
    };

    // --- Submit form via AJAX ---
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData(form);

        try {
            const response = await fetch(updateProfileUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });

            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (err) {
                console.error("Server returned HTML instead of JSON:", text);
                alert("Server error: see console for details");
                return;
            }

            if (data.success) {
                // Updated fields returned from backend
                const fields = ['fullname','dob','age','gender','phone','emergency_contact','address','email'];

                fields.forEach(f => {
                    const disp = document.getElementById(`display-${f}-text`);
                    const input = form.querySelector(`[name="${f}"]`);
                    if (disp) {
                        disp.innerText = data[f] !== null && data[f] !== undefined ? data[f] : 'Not Set';
                    }
                    if (input && f !== 'age') {
                        input.value = data[f] !== null && data[f] !== undefined ? data[f] : '';
                    }
                });

                toggleEdit(); // hide form, show display
                alert('Profile updated successfully.');
            } else {
                alert('Error: ' + data.message);
            }
        } catch (err) {
            console.error(err);
            alert('Network error: ' + err.message);
        }
    });
});
