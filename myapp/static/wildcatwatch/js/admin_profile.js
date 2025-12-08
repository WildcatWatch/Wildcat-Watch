document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profile-form');
    const display = document.getElementById('profile-display');
    const dobInput = form.querySelector('[name="dob"]');
    const ageInput = form.querySelector('[name="age"]');

    // Auto-calculate age from DOB
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

    // Toggle edit/display
    window.toggleEdit = function() {
        if (form.style.display === 'none' || form.style.display === '') {
            form.style.display = 'block';
            display.style.display = 'none';
        } else {
            form.style.display = 'none';
            display.style.display = 'block';
        }
    };

    // Submit form via AJAX
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

            const text = await response.text(); // always read as text first
            let data;
            try {
                data = JSON.parse(text); // then try parse as JSON
            } catch (err) {
                console.error("Server returned HTML instead of JSON:", text);
                alert("Server error: see console for details");
                return;
            }

            if (data.success) {
                // Update display fields
                const fields = ['fullname','dob','age','gender','blood_type','nationality','phone','emergency_contact','address','staff_id','work_schedule'];
                fields.forEach(f => {
                    const input = form.querySelector(`[name="${f}"]`);
                    const disp = document.getElementById(`display-${f}-text`);
                    if (input && disp) {
                        disp.innerText = input.value || 'Not Set';
                    }
                });
                toggleEdit();
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